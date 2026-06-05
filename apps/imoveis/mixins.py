import json

from apps.imoveis.localidades import BAIRROS


class LocalidadesFormMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bairros_json'] = BAIRROS
        context['bairros_selecionados_json'] = '[]'
        return context
