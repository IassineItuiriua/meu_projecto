from django import forms
from .models import Documento

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ('tipo', 'destino', 'finalidade')
        widgets = {
            'tipo': forms.Select(attrs={'class':'form-select'}),
            'destino': forms.TextInput(attrs={'class':'form-control'}),
            'finalidade': forms.TextInput(attrs={'class':'form-control'}),
        }
