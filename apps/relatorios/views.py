from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, View

from apps.imoveis.models import DemandaCliente, Imovel

IMOVEIS_HISTORICO_STATUS = ('vendido', 'alugado', 'reservado')


class HistoricoIndexView(TemplateView):
    template_name = 'historico/index.html'


class HistoricoImoveisView(TemplateView):
    template_name = 'historico/imoveis.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['imoveis'] = Imovel.objects.filter(
            status__in=IMOVEIS_HISTORICO_STATUS
        ).select_related('corretor').order_by('-finalizado_em', '-id')
        return context


class HistoricoDemandasView(TemplateView):
    template_name = 'historico/demandas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['demandas'] = DemandaCliente.objects.filter(
            status='atendida'
        ).select_related('cliente').order_by('-atendida_em', '-id')
        return context


class DemandaReabrirView(View):
    def post(self, request, pk):
        demanda = get_object_or_404(DemandaCliente, pk=pk, status='atendida')
        demanda.status = 'aberta'
        demanda.atendida_em = None
        demanda.save()
        messages.success(request, 'Demanda reaberta e movida para a listagem de demandas.')
        return redirect('demandas:list')
