from django.db.models import Count
from django.views.generic import TemplateView

from apps.imoveis.models import Cliente, Corretor, DemandaCliente, Imovel


class DashboardView(TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        imoveis = Imovel.objects.all()
        demandas = DemandaCliente.objects.select_related('cliente')

        context.update({
            'total_imoveis': imoveis.count(),
            'imoveis_disponiveis': imoveis.filter(status='disponivel').count(),
            'imoveis_vendidos': imoveis.filter(status='vendido').count(),
            'imoveis_reservados': imoveis.filter(status='reservado').count(),
            'imoveis_alugados': imoveis.filter(status='alugado').count(),
            'total_clientes': Cliente.objects.count(),
            'total_corretores': Corretor.objects.count(),
            'demandas_abertas': demandas.filter(status='aberta').count(),
            'demandas_atendidas': demandas.filter(status='atendida').count(),
            'ultimos_imoveis': imoveis.select_related('categoria').order_by('-id')[:5],
            'ultimas_demandas': demandas.order_by('-criado_em')[:5],
        })
        return context
