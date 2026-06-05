from django import forms
from apps.imoveis.models import Corretor

class CorretorForm(forms.ModelForm):
    class Meta:
        model = Corretor
        fields = ['nome', 'telefone', 'tipo', 'observacao']