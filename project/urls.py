from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('clientes/', include('apps.clientes.urls')),
    path('corretores/', include('apps.corretores.urls')),
    path('imoveis/', include('apps.imoveis.urls')),
    path('demandas/', include('apps.demandas.urls')),
    path('relatorios/', include('apps.relatorios.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)