from django import forms

from apps.imoveis.fields import MoedaDecimalField
from apps.imoveis.infra_utils import sincronizar_elevador_varanda
from .localidades import CIDADES, bairros_da_cidade
from .models import Imovel


class ImovelForm(forms.ModelForm):
    valor = MoedaDecimalField(label='Valor', required=True)
    valor_condominio = MoedaDecimalField(label='Valor do condomínio', required=False)

    class Meta:
        model = Imovel
        fields = [
            'titulo',
            'tipo',
            'finalidade',
            'cidade',
            'bairro',
            'endereco',
            'valor',
            'valor_condominio',
            'descricao',
            'area_total',
            'dormitorios',
            'suites',
            'banheiros',
            'vagas',
            'vagas_cobertas',
            'total_andares',
            'andar',
            'posicao_solar',
            'corretor',
            'infraestrutura',
            'status',
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
            'infraestrutura': forms.CheckboxSelectMultiple,
            'cidade': forms.Select(attrs={'id': 'id_cidade'}),
            'bairro': forms.Select(attrs={'id': 'id_bairro'}),
            'area_total': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'total_andares': forms.NumberInput(attrs={'min': '0'}),
            'andar': forms.NumberInput(attrs={'min': '0'}),
            'vagas': forms.NumberInput(attrs={'min': '0'}),
            'vagas_cobertas': forms.NumberInput(attrs={'min': '0'}),
            'dormitorios': forms.NumberInput(attrs={'min': '0'}),
            'suites': forms.NumberInput(attrs={'min': '0'}),
            'banheiros': forms.NumberInput(attrs={'min': '0'}),
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
        self.fields['area_total'].label = 'Área do imóvel (m²)'
        self.fields['total_andares'].label = 'Total de andares do prédio'
        self.fields['andar'].label = 'Andar do imóvel'
        self.fields['vagas'].label = 'Garagem'
        self.fields['vagas_cobertas'].label = 'Garagens cobertas'
        if self.instance.pk and self.instance.bairro:
            self.fields['bairro'].initial = self.instance.bairro

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('cidade'):
            self.add_error('cidade', 'Selecione a cidade.')
        if not cleaned_data.get('bairro'):
            self.add_error('bairro', 'Selecione o bairro.')
        vagas = cleaned_data.get('vagas') or 0
        vagas_cobertas = cleaned_data.get('vagas_cobertas') or 0
        if vagas_cobertas > vagas:
            self.add_error('vagas_cobertas', 'Garagens cobertas não pode ser maior que o total de garagem.')
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
            sincronizar_elevador_varanda(instance)
            instance.save(update_fields=['elevador', 'varanda'])
        return instance
