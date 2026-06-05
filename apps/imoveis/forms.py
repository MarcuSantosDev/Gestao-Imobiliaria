from django import forms
from .models import Imovel

class ImovelForm(forms.ModelForm):
    class Meta:
        model = Imovel
        fields = [
            'titulo',
            'categoria',
            'finalidade',
            'bairro',
            'endereco',
            'valor',
            'valor_condominio',
            'descricao',
            'status',
            'dormitorios',
            'suites',
            'banheiros',
            'vagas',
            'vagas_cobertas',
            'area_total',
            'area_construida',
            'andar',
            'elevador',
            'varanda',
            'posicao_solar',
            'corretor',
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
        }