from django import forms

from apps.imoveis.localidades import CIDADES, bairros_da_cidade
from apps.imoveis.models import DemandaCliente


class DemandaForm(forms.ModelForm):
    bairros_selecionados = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Bairros desejados',
    )

    class Meta:
        model = DemandaCliente
        fields = [
            'cliente',
            'tipo_imovel',
            'finalidade',
            'status',
            'valor_minimo',
            'valor_maximo',
            'cidade',
            'dormitorios',
            'vagas',
            'posicao_solar',
            'infraestrutura',
        ]
        widgets = {
            'infraestrutura': forms.CheckboxSelectMultiple,
            'cidade': forms.Select(attrs={'id': 'id_cidade'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cidade = self.data.get('cidade') or (self.instance.cidade if self.instance.pk else '')
        bairros = bairros_da_cidade(cidade)
        self.fields['cidade'].choices = [('', 'Selecione a cidade')] + [(c, c) for c in CIDADES]
        self.fields['bairros_selecionados'].choices = [(b, b) for b in bairros]
        if self.instance and self.instance.bairros:
            self.fields['bairros_selecionados'].initial = self.instance.get_bairros_lista()

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('cidade'):
            self.add_error('cidade', 'Selecione a cidade.')
        if not cleaned_data.get('bairros_selecionados'):
            self.add_error('bairros_selecionados', 'Selecione ao menos um bairro.')
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        bairros = self.cleaned_data.get('bairros_selecionados', [])
        instance.bairros = ', '.join(bairros)
        instance.bairro = bairros[0] if bairros else None
        if commit:
            instance.save()
            self.save_m2m()
        return instance
