from django.contrib import admin

from .models import (
    Cliente,
    Corretor,
    DemandaCliente,
    DemandaImovelSelecionado,
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
    list_display = ('nome', 'creci', 'telefone', 'tipo', 'imobiliaria')
    search_fields = ('nome', 'creci', 'imobiliaria')
    list_filter = ('tipo',)


@admin.register(Infraestrutura)
class InfraestruturaAdmin(admin.ModelAdmin):
    list_display = ('nome',)


class FotoImovelInline(admin.TabularInline):
    model = FotoImovel
    extra = 1


@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'cidade', 'bairro', 'valor', 'status', 'finalizado_em', 'corretor', 'created_by')
    list_filter = ('status', 'finalidade', 'tipo')
    search_fields = ('titulo', 'bairro')
    filter_horizontal = ('infraestrutura',)
    inlines = [FotoImovelInline]


class DemandaImovelSelecionadoInline(admin.TabularInline):
    model = DemandaImovelSelecionado
    extra = 0


@admin.register(DemandaCliente)
class DemandaClienteAdmin(admin.ModelAdmin):
    list_display = (
        'cliente', 'tipo_imovel', 'finalidade', 'cidade', 'status', 'criado_em', 'atendida_em',
    )
    list_filter = ('status', 'tipo_imovel', 'finalidade', 'elevador', 'varanda')
    filter_horizontal = ('infraestrutura',)
    inlines = [DemandaImovelSelecionadoInline]
