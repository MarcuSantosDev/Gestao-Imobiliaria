from django import template

from apps.imoveis.utils import formatar_moeda

register = template.Library()


@register.filter
def moeda(valor):
    return formatar_moeda(valor)
