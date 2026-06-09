from django.urls import path

from .views import (
    DemandaAtenderView,
    DemandaBuscaView,
    DemandaColaboradorRemoverView,
    DemandaCreateView,
    DemandaDeleteView,
    DemandaDetailView,
    DemandaImovelAdicionarView,
    DemandaImovelRemoverView,
    DemandaImoveisSelecionadosView,
    DemandaListView,
    DemandaUpdateView,
    NotificacaoActionView,
)

app_name = 'demandas'

urlpatterns = [
    path('', DemandaListView.as_view(), name='list'),
    path('novo/', DemandaCreateView.as_view(), name='create'),
    path('<int:pk>/', DemandaDetailView.as_view(), name='detail'),
    path('editar/<int:pk>/', DemandaUpdateView.as_view(), name='update'),
    path('deletar/<int:pk>/', DemandaDeleteView.as_view(), name='delete'),
    path('<int:pk>/buscar/', DemandaBuscaView.as_view(), name='buscar'),
    path('<int:pk>/atender/', DemandaAtenderView.as_view(), name='atender'),
    path('<int:pk>/imoveis-selecionados/', DemandaImoveisSelecionadosView.as_view(), name='imoveis_selecionados'),
    path('<int:pk>/imoveis/adicionar/', DemandaImovelAdicionarView.as_view(), name='imovel_adicionar'),
    path('<int:pk>/imoveis/<int:imovel_pk>/remover/', DemandaImovelRemoverView.as_view(), name='imovel_remover'),
    path('<int:pk>/colaboradores/<int:usuario_pk>/remover/', DemandaColaboradorRemoverView.as_view(), name='colaborador_remover'),
    path('notificacoes/<int:pk>/<str:action>/', NotificacaoActionView.as_view(), name='notification_action'),
]
