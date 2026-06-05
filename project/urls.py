from django.contrib import admin
from django.urls import path

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('clientes/', include('apps.clientes.urls')),
    path('corretores/', include('apps.corretores.urls')),
    path('imoveis/', include('apps.imoveis.urls')),
]