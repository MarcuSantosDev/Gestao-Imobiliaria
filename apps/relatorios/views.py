from django.db.models import Count
from django.views.generic import TemplateView

from apps.imoveis.models import Corretor, DemandaCliente, Imovel


class RelatoriosIndexView(TemplateView):
    template_name = 'relatorios/index.html'


class RelatorioImoveisView(TemplateView):
    template_name = 'relatorios/imoveis.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['imoveis'] = Imovel.objects.select_related('categoria', 'corretor').order_by('titulo')
        return context


class RelatorioCorretoresView(TemplateView):
    template_name = 'relatorios/corretores.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['corretores'] = Corretor.objects.annotate(
            total_imoveis=Count('imovel_set')
        ).order_by('nome')
        return context


class RelatorioDemandasView(TemplateView):
    template_name = 'relatorios/demandas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['demandas'] = DemandaCliente.objects.select_related('cliente').order_by('-criado_em')
        return context
