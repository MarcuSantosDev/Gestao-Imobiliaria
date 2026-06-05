from django import template

from apps.imoveis.fields import parse_moeda_br
from apps.imoveis.utils import formatar_moeda

register = template.Library()


@register.filter
def moeda(valor):
    return formatar_moeda(valor)


@register.filter
def moeda_input(valor):
    if not valor:
        return ''
    parsed = parse_moeda_br(valor)
    if parsed is None:
        return valor
    return formatar_moeda(parsed, simbolo=False)
