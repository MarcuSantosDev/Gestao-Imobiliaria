from django import forms

from .localidades import CIDADES, bairros_da_cidade
from .models import Imovel


class ImovelForm(forms.ModelForm):
    class Meta:
        model = Imovel
        fields = [
            'titulo',
            'categoria',
            'finalidade',
            'cidade',
            'bairro',
            'endereco',
            'valor',
            'descricao',
            'status',
            'dormitorios',
            'suites',
            'banheiros',
            'vagas',
            'posicao_solar',
            'corretor',
            'infraestrutura',
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
            'infraestrutura': forms.CheckboxSelectMultiple,
            'cidade': forms.Select(attrs={'id': 'id_cidade'}),
            'bairro': forms.Select(attrs={'id': 'id_bairro'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cidade = self.data.get('cidade') or (self.instance.cidade if self.instance.pk else '')
        bairros = bairros_da_cidade(cidade)
        self.fields['cidade'].choices = [('', 'Selecione a cidade')] + [(c, c) for c in CIDADES]
        self.fields['bairro'] = forms.ChoiceField(
            choices=[('', 'Selecione o bairro')] + [(b, b) for b in bairros],
            required=True,
            label='Bairro',
            widget=forms.Select(attrs={'id': 'id_bairro'}),
        )
        self.fields['cidade'].required = True
        if self.instance.pk and self.instance.bairro:
            self.fields['bairro'].initial = self.instance.bairro

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('cidade'):
            self.add_error('cidade', 'Selecione a cidade.')
        if not cleaned_data.get('bairro'):
            self.add_error('bairro', 'Selecione o bairro.')
        return cleaned_data
