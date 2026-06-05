from django.urls import path

from .views import (
    RelatorioCorretoresView,
    RelatorioDemandasView,
    RelatorioImoveisView,
    RelatoriosIndexView,
)

app_name = 'relatorios'

urlpatterns = [
    path('', RelatoriosIndexView.as_view(), name='index'),
    path('imoveis/', RelatorioImoveisView.as_view(), name='imoveis'),
    path('corretores/', RelatorioCorretoresView.as_view(), name='corretores'),
    path('demandas/', RelatorioDemandasView.as_view(), name='demandas'),
]
