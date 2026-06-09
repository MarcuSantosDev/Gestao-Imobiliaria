import json

from django.contrib import messages
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from apps.imoveis.localidades import BAIRROS
from apps.imoveis.mixins import LocalidadesFormMixin
from apps.imoveis.models import DemandaCliente, DemandaImovelSelecionado, Imovel

from .forms import DemandaForm
from .matching import buscar_imoveis_compativeis


def queryset_demandas_abertas():
    return DemandaCliente.objects.filter(status__in=DemandaCliente.STATUS_ABERTAS)


class DemandaListView(ListView):
    model = DemandaCliente
    template_name = 'demandas/list.html'
    context_object_name = 'demandas'

    def get_queryset(self):
        qs = (
            queryset_demandas_abertas()
            .select_related('cliente')
            .annotate(total_imoveis=Count('imoveis_selecionados'))
        )
        busca = self.request.GET.get('q', '').strip()
        if busca:
            qs = qs.filter(cliente__nome__icontains=busca)
        return qs.order_by('-criado_em')


class DemandaDetailView(DetailView):
    model = DemandaCliente
    template_name = 'demandas/detail.html'
    context_object_name = 'demanda'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.esta_no_historico():
            messages.info(request, 'Esta demanda está no histórico.')
            return redirect('historico:demandas')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['imoveis_selecionados'] = self.object.get_imoveis_selecionados()
        return context


class DemandaFormMixin(LocalidadesFormMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object and self.object.pk:
            context['bairros_selecionados_json'] = json.dumps(self.object.get_bairros_lista())
        return context


class DemandaCreateView(DemandaFormMixin, CreateView):
    model = DemandaCliente
    form_class = DemandaForm
    template_name = 'demandas/form.html'
    success_url = reverse_lazy('demandas:list')


class DemandaUpdateView(DemandaFormMixin, UpdateView):
    model = DemandaCliente
    form_class = DemandaForm
    template_name = 'demandas/form.html'
    success_url = reverse_lazy('demandas:list')

    def get_queryset(self):
        return queryset_demandas_abertas()

    def form_valid(self, form):
        self.object = form.save()
        if self.object.status == 'atendida':
            messages.success(self.request, 'Demanda finalizada e movida para o histórico.')
            return redirect('historico:demandas')
        if self.object.status == 'cancelado':
            messages.success(self.request, 'Demanda cancelada e movida para o histórico.')
            return redirect('historico:demandas')
        messages.success(self.request, 'Demanda atualizada com sucesso.')
        return redirect(self.success_url)


class DemandaDeleteView(DeleteView):
    model = DemandaCliente
    template_name = 'demandas/confirm_delete.html'
    success_url = reverse_lazy('demandas:list')

    def get_queryset(self):
        return queryset_demandas_abertas()


class DemandaBuscaView(DetailView):
    model = DemandaCliente
    template_name = 'demandas/busca.html'
    context_object_name = 'demanda'

    def get_queryset(self):
        return queryset_demandas_abertas()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resultados'] = buscar_imoveis_compativeis(self.object)
        context['imoveis_selecionados_ids'] = set(
            self.object.imoveis_selecionados.values_list('imovel_id', flat=True)
        )
        context['total_selecionados'] = len(context['imoveis_selecionados_ids'])
        return context


class DemandaImoveisSelecionadosView(DetailView):
    model = DemandaCliente
    template_name = 'demandas/imoveis_selecionados.html'
    context_object_name = 'demanda'

    def get_queryset(self):
        return queryset_demandas_abertas()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['imoveis_selecionados'] = self.object.get_imoveis_selecionados()
        return context


@method_decorator(require_POST, name='dispatch')
class DemandaImovelAdicionarView(View):
    def post(self, request, pk):
        demanda = get_object_or_404(DemandaCliente, pk=pk, status__in=DemandaCliente.STATUS_ABERTAS)
        imovel = get_object_or_404(Imovel, pk=request.POST.get('imovel_id'))
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')

        if imovel.status != 'disponivel':
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'ok': False, 'error': 'Somente imóveis disponíveis podem ser adicionados à demanda.'}, status=400)
            messages.error(request, 'Somente imóveis disponíveis podem ser adicionados à demanda.')
            return redirect(next_url or reverse_lazy('imoveis:detail', kwargs={'pk': imovel.pk}))

        selecao, criado = DemandaImovelSelecionado.objects.get_or_create(
            demanda=demanda,
            imovel=imovel,
        )
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'ok': True,
                'criado': criado,
                'total': demanda.imoveis_selecionados.count(),
            })
        if criado:
            messages.success(request, f'Imóvel "{imovel.titulo}" adicionado à demanda.')
        else:
            messages.info(request, 'Este imóvel já estava selecionado.')
        if next_url:
            return redirect(next_url)
        return redirect('demandas:imoveis_selecionados', pk=demanda.pk)


@method_decorator(require_POST, name='dispatch')
class DemandaImovelRemoverView(View):
    def post(self, request, pk, imovel_pk):
        demanda = get_object_or_404(DemandaCliente, pk=pk, status__in=DemandaCliente.STATUS_ABERTAS)
        selecao = get_object_or_404(
            DemandaImovelSelecionado,
            demanda=demanda,
            imovel_id=imovel_pk,
        )
        titulo = selecao.imovel.titulo
        selecao.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'ok': True,
                'total': demanda.imoveis_selecionados.count(),
            })
        messages.success(request, f'Imóvel "{titulo}" removido da demanda.')
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
        if next_url:
            return redirect(next_url)
        return redirect('demandas:imoveis_selecionados', pk=demanda.pk)


class DemandaAtenderView(View):
    def post(self, request, pk):
        demanda = get_object_or_404(DemandaCliente, pk=pk, status__in=DemandaCliente.STATUS_ABERTAS)
        demanda.status = 'atendida'
        demanda.atendida_em = timezone.now()
        demanda.save()
        messages.success(request, 'Demanda finalizada e movida para o histórico.')
        return redirect('historico:demandas')
