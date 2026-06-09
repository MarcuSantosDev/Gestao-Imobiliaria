from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView, TemplateView, View

from apps.imoveis.models import DemandaCliente, Imovel

IMOVEIS_HISTORICO_STATUS = ('vendido',)


class HistoricoOrdenacaoMixin:
    campo_data = None
    paginate_by = 10

    def get_ordem(self):
        ordem = self.request.GET.get('ordem', 'recente')
        return ordem if ordem in ('recente', 'antigo') else 'recente'

    def ordenar_queryset(self, qs):
        if self.get_ordem() == 'antigo':
            return qs.order_by(self.campo_data, 'id')
        return qs.order_by(f'-{self.campo_data}', '-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ordem = self.get_ordem()
        context['ordem'] = ordem
        context['ordem_proxima'] = 'antigo' if ordem == 'recente' else 'recente'
        return context


class HistoricoIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'historico/index.html'


class HistoricoImoveisView(LoginRequiredMixin, HistoricoOrdenacaoMixin, ListView):
    model = Imovel
    template_name = 'historico/imoveis.html'
    context_object_name = 'imoveis'
    campo_data = 'finalizado_em'

    def get_queryset(self):
        qs = Imovel.objects.filter(
            status__in=IMOVEIS_HISTORICO_STATUS
        ).select_related('corretor', 'created_by')
        return self.ordenar_queryset(qs)


class HistoricoDemandasView(LoginRequiredMixin, HistoricoOrdenacaoMixin, ListView):
    model = DemandaCliente
    template_name = 'historico/demandas.html'
    context_object_name = 'demandas'
    campo_data = 'atendida_em'

    def get_queryset(self):
        qs = DemandaCliente.objects.filter(
            status__in=DemandaCliente.STATUS_HISTORICO,
        ).select_related('cliente').prefetch_related('colaboradores')
        return self.ordenar_queryset(qs)


class HistoricoDemandaDetailView(LoginRequiredMixin, DetailView):
    model = DemandaCliente
    template_name = 'historico/demanda_detail.html'
    context_object_name = 'demanda'

    def get_queryset(self):
        return DemandaCliente.objects.filter(status__in=DemandaCliente.STATUS_HISTORICO).select_related('cliente').prefetch_related('colaboradores')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['imoveis'] = self.object.get_imoveis_selecionados()
        return context


class HistoricoImovelReabrirView(View):
    def post(self, request, pk):
        imovel = get_object_or_404(
            Imovel,
            pk=pk,
            status__in=IMOVEIS_HISTORICO_STATUS,
        )
        imovel.status = 'disponivel'
        imovel.finalizado_em = None
        imovel.save(update_fields=['status', 'finalizado_em'])
        imovel.selecoes_demanda.all().delete()
        messages.success(request, 'Imóvel reaberto e movido para a listagem de imóveis.')
        return redirect('historico:imoveis')


class DemandaReabrirView(View):
    def post(self, request, pk):
        demanda = get_object_or_404(
            DemandaCliente,
            pk=pk,
            status__in=DemandaCliente.STATUS_HISTORICO,
        )
        demanda.status = 'aberta'
        demanda.atendida_em = None
        demanda.save()
        messages.success(request, 'Demanda reaberta e movida para a listagem de demandas.')
        return redirect('demandas:list')
