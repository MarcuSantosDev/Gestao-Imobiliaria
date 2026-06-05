from django.urls import path
from .views import *

app_name = 'imoveis'

urlpatterns = [
    path('', ImovelListView.as_view(), name='list'),
    path('novo/', ImovelCreateView.as_view(), name='create'),
    path('<int:pk>/', ImovelDetailView.as_view(), name='detail'),
    path('editar/<int:pk>/', ImovelUpdateView.as_view(), name='update'),
    path('deletar/<int:pk>/', ImovelDeleteView.as_view(), name='delete'),
]