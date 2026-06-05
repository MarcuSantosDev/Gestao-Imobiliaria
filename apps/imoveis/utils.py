from decimal import Decimal, InvalidOperation


def formatar_moeda(valor, simbolo=True):
    if valor is None or valor == '':
        return '—'
    try:
        numero = Decimal(str(valor))
        texto = f'{numero:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
        return f'R$ {texto}' if simbolo else texto
    except (InvalidOperation, ValueError, TypeError):
        return str(valor)
