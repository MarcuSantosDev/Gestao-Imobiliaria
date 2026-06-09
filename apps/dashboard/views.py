from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.utils import timezone
from django.views.generic import TemplateView

from apps.imoveis.models import Cliente, Corretor, DemandaCliente, Imovel


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agora = timezone.localtime()
        usuario = self.request.user

        imoveis = Imovel.objects.all()
        demandas = DemandaCliente.objects.select_related('cliente')
        demandas_usuario = demandas.filter(Q(owner=usuario) | Q(colaboradores=usuario)).distinct()

        context.update({
            'total_imoveis': imoveis.count(),
            'imoveis_disponiveis': imoveis.filter(status='disponivel').count(),
            'imoveis_vendidos': imoveis.filter(status='vendido').count(),
            'imoveis_reservados': imoveis.filter(status='reservado').count(),
            'imoveis_alugados': imoveis.filter(status='alugado').count(),
            'total_clientes': Cliente.objects.count(),
            'total_corretores': Corretor.objects.count(),
            'demandas_abertas': demandas_usuario.filter(status__in=DemandaCliente.STATUS_ABERTAS).count(),
            'demandas_atendidas_mes': demandas_usuario.filter(
                status='atendida',
                atendida_em__year=agora.year,
                atendida_em__month=agora.month,
            ).count(),
            'agora': agora,
            'ultimos_imoveis': Imovel.objects.filter(created_by=usuario).order_by('-id')[:5],
            'ultimas_demandas': demandas_usuario.filter(
                status__in=DemandaCliente.STATUS_ABERTAS,
            ).order_by('-criado_em')[:5],
        })
        return context
