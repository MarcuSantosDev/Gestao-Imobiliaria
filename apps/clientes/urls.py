from django.urls import path
from .views import *

app_name = 'clientes'

urlpatterns = [
    path('', ClienteListView.as_view(), name='list'),
    path('novo/', ClienteCreateView.as_view(), name='create'),
    path('editar/<int:pk>/', ClienteUpdateView.as_view(), name='update'),
    path('deletar/<int:pk>/', ClienteDeleteView.as_view(), name='delete'),
]