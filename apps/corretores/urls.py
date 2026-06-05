from django.urls import path
from .views import *

app_name = 'corretores'

urlpatterns = [
    path('', CorretorListView.as_view(), name='list'),
    path('novo/', CorretorCreateView.as_view(), name='create'),
    path('editar/<int:pk>/', CorretorUpdateView.as_view(), name='update'),
    path('deletar/<int:pk>/', CorretorDeleteView.as_view(), name='delete'),
]