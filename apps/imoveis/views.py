from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from apps.imoveis.fields import parse_moeda_br

from apps.imoveis.localidades import BAIRROS, CIDADES, bairros_da_cidade
from .forms import ImovelForm
from .mixins import LocalidadesFormMixin
from .models import FotoImovel, Imovel
from .sharing import gerar_texto_compartilhamento

import io
import os
import zipfile

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator


class ImovelListView(ListView):
    model = Imovel
    template_name = 'imoveis/list.html'
    context_object_name = 'imoveis'
    paginate_by = 10

    def get_queryset(self):
        qs = Imovel.objects.select_related('corretor').prefetch_related('fotos')
        params = self.request.GET

        if q := params.get('q', '').strip():
            qs = qs.filter(titulo__icontains=q)
        if cidade := params.get('cidade', '').strip():
            qs = qs.filter(cidade=cidade)
        if bairro := params.get('bairro', '').strip():
            qs = qs.filter(bairro=bairro)
        if finalidade := params.get('finalidade', '').strip():
            qs = qs.filter(finalidade=finalidade)
        if status := params.get('status', '').strip():
            qs = qs.filter(status=status)
        if tipo := params.get('tipo', '').strip():
            qs = qs.filter(tipo=tipo)
        if valor_min := params.get('valor_min', '').strip():
            parsed = parse_moeda_br(valor_min)
            if parsed is not None:
                qs = qs.filter(valor__gte=parsed)
        if valor_max := params.get('valor_max', '').strip():
            parsed = parse_moeda_br(valor_max)
            if parsed is not None:
                qs = qs.filter(valor__lte=parsed)

        return qs.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cidade = self.request.GET.get('cidade', '')
        context['bairros_json'] = BAIRROS
        context['cidades'] = CIDADES
        context['tipo_choices'] = Imovel.TIPO_CHOICES
        context['bairros_filtro'] = bairros_da_cidade(cidade) if cidade else []
        context['finalidade_choices'] = Imovel.FINALIDADE_CHOICES
        context['status_choices'] = Imovel.STATUS_CHOICES
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
