import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
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


def queryset_demandas_abertas(user=None):
    qs = DemandaCliente.objects.filter(status__in=DemandaCliente.STATUS_ABERTAS)
    if user is not None:
        qs = qs.filter(owner=user)
    return qs


class DemandaListView(LoginRequiredMixin, ListView):
    model = DemandaCliente
    template_name = 'demandas/list.html'
    context_object_name = 'demandas'

    def get_queryset(self):
        qs = (
            queryset_demandas_abertas(self.request.user)
            .select_related('cliente')
            .annotate(total_imoveis=Count('imoveis_selecionados'))
        )
        busca = self.request.GET.get('q', '').strip()
        if busca:
            qs = qs.filter(cliente__nome__icontains=busca)
        return qs.order_by('-criado_em')


class DemandaDetailView(LoginRequiredMixin, DetailView):
    model = DemandaCliente
    template_name = 'demandas/detail.html'
    context_object_name = 'demanda'

    def get_queryset(self):
        return queryset_demandas_abertas(self.request.user).select_related('cliente')

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


class DemandaCreateView(LoginRequiredMixin, DemandaFormMixin, CreateView):
    model = DemandaCliente
    form_class = DemandaForm
    template_name = 'demandas/form.html'
    success_url = reverse_lazy('demandas:list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class DemandaUpdateView(LoginRequiredMixin, DemandaFormMixin, UpdateView):
    model = DemandaCliente
    form_class = DemandaForm
    template_name = 'demandas/form.html'
    success_url = reverse_lazy('demandas:list')

    def get_queryset(self):
        return queryset_demandas_abertas(self.request.user)

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


class DemandaDeleteView(LoginRequiredMixin, DeleteView):
    model = DemandaCliente
    template_name = 'demandas/confirm_delete.html'
    success_url = reverse_lazy('demandas:list')

    def get_queryset(self):
        return queryset_demandas_abertas(self.request.user)


class DemandaBuscaView(LoginRequiredMixin, DetailView):
    model = DemandaCliente
    template_name = 'demandas/busca.html'
    context_object_name = 'demanda'

    def get_queryset(self):
        return queryset_demandas_abertas(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resultados'] = buscar_imoveis_compativeis(self.object)
        context['imoveis_selecionados_ids'] = set(
            self.object.imoveis_selecionados.values_list('imovel_id', flat=True)
        )
        context['total_selecionados'] = len(context['imoveis_selecionados_ids'])
        return context


class DemandaImoveisSelecionadosView(LoginRequiredMixin, DetailView):
    model = DemandaCliente
    template_name = 'demandas/imoveis_selecionados.html'
    context_object_name = 'demanda'

    def get_queryset(self):
        return queryset_demandas_abertas(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['imoveis_selecionados'] = self.object.get_imoveis_selecionados()
        return context


@method_decorator(require_POST, name='dispatch')
class DemandaImovelAdicionarView(LoginRequiredMixin, View):
    def post(self, request, pk):
        demanda = get_object_or_404(
            DemandaCliente,
            pk=pk,
            owner=request.user,
            status__in=DemandaCliente.STATUS_ABERTAS,
        )
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
class DemandaImovelRemoverView(LoginRequiredMixin, View):
    def post(self, request, pk, imovel_pk):
        demanda = get_object_or_404(
            DemandaCliente,
            pk=pk,
            owner=request.user,
            status__in=DemandaCliente.STATUS_ABERTAS,
        )
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


class DemandaAtenderView(LoginRequiredMixin, View):
    def post(self, request, pk):
        demanda = get_object_or_404(
            DemandaCliente,
            pk=pk,
            owner=request.user,
            status__in=DemandaCliente.STATUS_ABERTAS,
        )
        selecionados = demanda.get_imoveis_selecionados()
        if not selecionados.exists():
            messages.error(request, 'Não é possível finalizar a demanda sem pelo menos um imóvel selecionado.')
            return redirect('demandas:detail', pk=demanda.pk)
        if not selecionados.filter(status__in=Imovel.HISTORICO_STATUS).exists():
            messages.error(request, 'Só é possível finalizar a demanda quando um imóvel selecionado estiver vendido ou alugado.')
            return redirect('demandas:detail', pk=demanda.pk)

        demanda.status = 'atendida'
        demanda.atendida_em = timezone.now()
        demanda.save()
        messages.success(request, 'Demanda finalizada e movida para o histórico.')
        return redirect('historico:demandas')
