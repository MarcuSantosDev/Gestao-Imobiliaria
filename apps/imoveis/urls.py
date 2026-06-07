from django.urls import path
from .views import *

app_name = 'imoveis'

urlpatterns = [
    path('', ImovelListView.as_view(), name='list'),
    path('novo/', ImovelCreateView.as_view(), name='create'),
    path('foto/<int:foto_pk>/excluir/', FotoImovelDeleteView.as_view(), name='foto_delete'),
    path('foto/<int:foto_pk>/recortar/', FotoImovelCropView.as_view(), name='foto_crop'),
    path('<int:pk>/', ImovelDetailView.as_view(), name='detail'),
    path('editar/<int:pk>/', ImovelUpdateView.as_view(), name='update'),
    path('deletar/<int:pk>/', ImovelDeleteView.as_view(), name='delete'),
    path('<int:pk>/compartilhar/texto/', ImovelCompartilharTextoView.as_view(), name='compartilhar_texto'),
    path('<int:pk>/compartilhar/fotos/', ImovelCompartilharFotosView.as_view(), name='compartilhar_fotos'),
]