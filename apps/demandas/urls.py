from django.urls import path

from .views import (
    DemandaAtenderView,
    DemandaBuscaView,
    DemandaCreateView,
    DemandaDeleteView,
    DemandaDetailView,
    DemandaListView,
    DemandaUpdateView,
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
]
