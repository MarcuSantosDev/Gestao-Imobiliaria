from django import forms
from apps.imoveis.models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'telefone', 'email', 'observacao']
        widgets = {
            'observacao': forms.Textarea(attrs={'rows': 3}),
        }