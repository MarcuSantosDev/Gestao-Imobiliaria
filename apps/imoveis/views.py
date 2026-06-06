from decimal import Decimal, InvalidOperation

from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from apps.imoveis.fields import parse_moeda_br

from apps.imoveis.localidades import BAIRROS, CIDADES, bairros_da_cidade
from .forms import ImovelForm
from .mixins import LocalidadesFormMixin
from .models import Corretor, FotoImovel, Imovel, Infraestrutura
from .sharing import gerar_texto_compartilhamento

import io
import os
import zipfile

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator


def _parse_int(value):
    if value in (None, ''):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_decimal(value):
    if value in (None, ''):
        return None
    try:
        return Decimal(str(value).replace(',', '.'))
    except (InvalidOperation, ValueError):
        return None


class ImovelListView(ListView):
    model = Imovel
    template_name = 'imoveis/list.html'
    context_object_name = 'imoveis'
    paginate_by = 10

    def get_queryset(self):
        qs = Imovel.objects.select_related('corretor').prefetch_related('fotos', 'infraestrutura')
        params = self.request.GET

        if q := params.get('q', '').strip():
            qs = qs.filter(titulo__icontains=q)
        if cidade := params.get('cidade', '').strip():
            qs = qs.filter(cidade=cidade)
        if bairro := params.get('bairro', '').strip():
            qs = qs.filter(bairro=bairro)
        if endereco := params.get('endereco', '').strip():
            qs = qs.filter(endereco__icontains=endereco)
        if finalidade := params.get('finalidade', '').strip():
            qs = qs.filter(finalidade=finalidade)
        if status := params.get('status', '').strip():
            qs = qs.filter(status=status)
        if tipo := params.get('tipo', '').strip():
            qs = qs.filter(tipo=tipo)
        if corretor := params.get('corretor', '').strip():
            qs = qs.filter(corretor_id=corretor)
        if posicao := params.get('posicao_solar', '').strip():
            qs = qs.filter(posicao_solar=posicao)

        for campo, filtro in (
            ('valor_min', 'valor__gte'),
            ('valor_max', 'valor__lte'),
            ('condominio_min', 'valor_condominio__gte'),
            ('condominio_max', 'valor_condominio__lte'),
        ):
            if raw := params.get(campo, '').strip():
                parsed = parse_moeda_br(raw)
                if parsed is not None:
                    qs = qs.filter(**{filtro: parsed})

        if area_min := _parse_decimal(params.get('area_min')):
            qs = qs.filter(area_total__gte=area_min)
        if area_max := _parse_decimal(params.get('area_max')):
            qs = qs.filter(area_total__lte=area_max)

        for campo, filtro in (
            ('dormitorios_min', 'dormitorios__gte'),
            ('suites_min', 'suites__gte'),
            ('banheiros_min', 'banheiros__gte'),
            ('vagas_min', 'vagas__gte'),
            ('vagas_cobertas_min', 'vagas_cobertas__gte'),
            ('total_andares_min', 'total_andares__gte'),
            ('andar', 'andar'),
        ):
            if valor := _parse_int(params.get(campo)):
                qs = qs.filter(**{filtro: valor})

        if elevador := params.get('elevador', '').strip():
            qs = qs.filter(elevador=(elevador == 'sim'))
        if varanda := params.get('varanda', '').strip():
            qs = qs.filter(varanda=(varanda == 'sim'))

        infra_ids = [i for i in (_parse_int(v) for v in params.getlist('infraestrutura')) if i]
        for infra_id in infra_ids:
            qs = qs.filter(infraestrutura__id=infra_id)

        return qs.distinct().order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cidade = self.request.GET.get('cidade', '')
        context['bairros_json'] = BAIRROS
        context['cidades'] = CIDADES
        context['tipo_choices'] = Imovel.TIPO_CHOICES
        context['bairros_filtro'] = bairros_da_cidade(cidade) if cidade else []
        context['finalidade_choices'] = Imovel.FINALIDADE_CHOICES
        context['status_choices'] = Imovel.STATUS_CHOICES
        context['posicao_solar_choices'] = Imovel.POSICAO_SOLAR_CHOICES
        context['corretores'] = Corretor.objects.order_by('nome')
        context['infraestruturas'] = Infraestrutura.objects.order_by('nome')
        context['sim_nao_choices'] = (('sim', 'Sim'), ('nao', 'Não'))
        context['infraestrutura_selecionada'] = self.request.GET.getlist('infraestrutura')
        params = self.request.GET
        avancados = 0
        for campo in (
            'endereco', 'corretor', 'condominio_min', 'condominio_max',
            'area_min', 'area_max', 'posicao_solar', 'dormitorios_min',
            'suites_min', 'banheiros_min', 'vagas_min', 'vagas_cobertas_min',
            'total_andares_min', 'andar', 'elevador', 'varanda',
        ):
            if params.get(campo, '').strip():
                avancados += 1
        avancados += len(params.getlist('infraestrutura'))
        context['filtros_avancados_ativos'] = avancados
        return context


class ImovelDetailView(DetailView):
    model = Imovel
    template_name = 'imoveis/detail.html'
    context_object_name = 'imovel'

    def get_queryset(self):
        return super().get_queryset().select_related('corretor').prefetch_related(
            'fotos', 'infraestrutura'
        )


class ImovelCreateView(LocalidadesFormMixin, CreateView):
    model = Imovel
    form_class = ImovelForm
    template_name = 'imoveis/form.html'
    success_url = reverse_lazy('imoveis:list')

    def form_valid(self, form):
        response = super().form_valid(form)
        self._salvar_fotos(self.object)
        return response

    def _salvar_fotos(self, imovel):
        for foto in self.request.FILES.getlist('fotos'):
            FotoImovel.objects.create(imovel=imovel, imagem=foto)


class ImovelUpdateView(LocalidadesFormMixin, UpdateView):
    model = Imovel
    form_class = ImovelForm
    template_name = 'imoveis/form.html'
    success_url = reverse_lazy('imoveis:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fotos_existentes'] = self.object.fotos.all()
        context['total_fotos'] = self.object.fotos.count()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        self._salvar_fotos(self.object)
        return response

    def _salvar_fotos(self, imovel):
        for foto in self.request.FILES.getlist('fotos'):
            FotoImovel.objects.create(imovel=imovel, imagem=foto)


class ImovelDeleteView(DeleteView):
    model = Imovel
    template_name = 'imoveis/confirm_delete.html'
    success_url = reverse_lazy('imoveis:list')


class ImovelCompartilharTextoView(View):
    def get(self, request, pk):
        imovel = Imovel.objects.select_related('corretor').prefetch_related('infraestrutura').get(pk=pk)
        return JsonResponse({'texto': gerar_texto_compartilhamento(imovel)})


class ImovelCompartilharFotosView(View):
    def get(self, request, pk):
        imovel = Imovel.objects.prefetch_related('fotos').get(pk=pk)
        buffer = io.BytesIO()

        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i, foto in enumerate(imovel.fotos.all(), start=1):
                if foto.imagem:
                    ext = os.path.splitext(foto.imagem.name)[1] or '.jpg'
                    zf.writestr(f'foto_{i}{ext}', foto.imagem.read())

        nome_arquivo = f"{imovel.titulo.replace(' ', '_')}.zip"
        response = HttpResponse(buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
        return response


@method_decorator(require_POST, name='dispatch')
class FotoImovelDeleteView(View):
    def post(self, request, foto_pk):
        foto = get_object_or_404(FotoImovel, pk=foto_pk)
        imovel_id = foto.imovel_id
        if foto.imagem:
            foto.imagem.delete(save=False)
        foto.delete()
        total = FotoImovel.objects.filter(imovel_id=imovel_id).count()
        return JsonResponse({'ok': True, 'total_fotos': total})
