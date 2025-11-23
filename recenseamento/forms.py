from django import forms
from .models import Recenseamento
from django.core.exceptions import ValidationError
import re

class RecenseamentoForm(forms.ModelForm):
    class Meta:
        model = Recenseamento
        fields = (
            'nome_completo', 'filiacao_pai', 'filiacao_mae', 'data_nascimento',
            'nacionalidade', 'naturalidade', 'morada', 'telefone', 
            'email', 'contacto_familiar', 'documento_identidade'
        )
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'filiacao_pai': forms.TextInput(attrs={'class': 'form-control'}),
            'filiacao_mae': forms.TextInput(attrs={'class': 'form-control'}),
            'nacionalidade': forms.TextInput(attrs={'class': 'form-control'}),
            'naturalidade': forms.TextInput(attrs={'class': 'form-control'}),
            'morada': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contacto_familiar': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_numero_telefone(self):
        numero = self.cleaned_data.get('telefone')
        if not re.match(r'^\+?\d{9,15}$', numero):
            raise ValidationError("Número de telefone inválido. Ex: +258841234567")
        return numero
