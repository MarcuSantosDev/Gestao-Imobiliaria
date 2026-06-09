from django.urls import path

from .views import (
    DemandaReabrirView,
    HistoricoDemandaDetailView,
    HistoricoDemandasView,
    HistoricoImovelReabrirView,
    HistoricoImoveisView,
    HistoricoIndexView,
)

app_name = 'historico'

urlpatterns = [
    path('', HistoricoIndexView.as_view(), name='index'),
    path('imoveis/', HistoricoImoveisView.as_view(), name='imoveis'),
    path('imoveis/<int:pk>/reabrir/', HistoricoImovelReabrirView.as_view(), name='imoveis_reabrir'),
    path('demandas/', HistoricoDemandasView.as_view(), name='demandas'),
    path('demandas/<int:pk>/', HistoricoDemandaDetailView.as_view(), name='demandas_detail'),
    path('demandas/<int:pk>/reabrir/', DemandaReabrirView.as_view(), name='demandas_reabrir'),
]
