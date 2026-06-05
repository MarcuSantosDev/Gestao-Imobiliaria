from django.urls import path

from .views import (
    DemandaReabrirView,
    HistoricoDemandasView,
    HistoricoImoveisView,
    HistoricoIndexView,
)

app_name = 'historico'

urlpatterns = [
    path('', HistoricoIndexView.as_view(), name='index'),
    path('imoveis/', HistoricoImoveisView.as_view(), name='imoveis'),
    path('demandas/', HistoricoDemandasView.as_view(), name='demandas'),
    path('demandas/<int:pk>/reabrir/', DemandaReabrirView.as_view(), name='demandas_reabrir'),
]
