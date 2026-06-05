from decimal import Decimal, InvalidOperation

from django import forms

from .utils import formatar_moeda


def parse_moeda_br(valor):
    if valor is None or valor == '':
        return None
    texto = str(valor).replace('R$', '').strip().replace(' ', '')
    if not texto:
        return None
    if ',' in texto:
        texto = texto.replace('.', '').replace(',', '.')
    try:
        return Decimal(texto)
    except InvalidOperation:
        return None


class MoedaDecimalField(forms.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_digits', 12)
        kwargs.setdefault('decimal_places', 2)
        kwargs.setdefault('required', False)
        kwargs.setdefault(
            'widget',
            forms.TextInput(attrs={
                'class': 'form-control moeda-input',
                'inputmode': 'decimal',
                'placeholder': '0,00',
                'autocomplete': 'off',
            }),
        )
        super().__init__(*args, **kwargs)

    def prepare_value(self, value):
        if value in (None, ''):
            return ''
        try:
            return formatar_moeda(value, simbolo=False)
        except (InvalidOperation, ValueError, TypeError):
            return value

    def to_python(self, value):
        if value in (None, ''):
            return None
        parsed = parse_moeda_br(value)
        if parsed is None:
            raise forms.ValidationError('Informe um valor monetário válido.')
        return super().to_python(str(parsed))
