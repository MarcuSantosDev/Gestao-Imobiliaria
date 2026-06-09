from django import forms

from apps.imoveis.models import Corretor


class CorretorForm(forms.ModelForm):
    class Meta:
        model = Corretor
        fields = ['nome', 'telefone', 'creci', 'tipo', 'imobiliaria', 'observacao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'creci': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'id': 'id_tipo', 'class': 'form-select'}),
            'imobiliaria': forms.TextInput(attrs={'id': 'id_imobiliaria', 'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['creci'].label = 'CRECI'
        self.fields['imobiliaria'].label = 'Imobiliária'

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        imobiliaria = (cleaned_data.get('imobiliaria') or '').strip()
        if tipo == 'imobiliaria' and not imobiliaria:
            self.add_error('imobiliaria', 'Informe de qual imobiliária o corretor faz parte.')
        if tipo == 'autonomo':
            cleaned_data['imobiliaria'] = None
        else:
            cleaned_data['imobiliaria'] = imobiliaria
        return cleaned_data
