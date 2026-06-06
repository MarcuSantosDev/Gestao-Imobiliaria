from django import template

register = template.Library()


@register.filter
def filtro_obrigatorio(demanda, chave):
    return demanda.filtro_e_obrigatorio(chave)
