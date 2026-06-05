from django.contrib import admin

from .models import (
    Categoria,
    Cliente,
    Corretor,
    DemandaCliente,
    FotoImovel,
    Imovel,
    Infraestrutura,
)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'email', 'criado_em')
    search_fields = ('nome', 'telefone')


@admin.register(Corretor)
class CorretorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'tipo')
    search_fields = ('nome',)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)


@admin.register(Infraestrutura)
class InfraestruturaAdmin(admin.ModelAdmin):
    list_display = ('nome',)


class FotoImovelInline(admin.TabularInline):
    model = FotoImovel
    extra = 1


@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'cidade', 'bairro', 'valor', 'status', 'corretor')
    list_filter = ('status', 'finalidade', 'categoria')
    search_fields = ('titulo', 'bairro')
    filter_horizontal = ('infraestrutura',)
    inlines = [FotoImovelInline]


@admin.register(DemandaCliente)
class DemandaClienteAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo_imovel', 'finalidade', 'cidade', 'status', 'criado_em', 'atendida_em')
    list_filter = ('status', 'tipo_imovel', 'finalidade')
    filter_horizontal = ('infraestrutura',)
