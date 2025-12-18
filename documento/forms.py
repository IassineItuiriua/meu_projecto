from django import forms
from .models import Documento


class SolicitarDocumentoForm(forms.ModelForm):
    """
    Formulário final para solicitação de documentos militares.
    Inclui campos adicionais usados na validação:
    - bi (para verificar recenseamento)
    - data_nascimento (para confirmar identidade se não tiver Recenseamento)
    """

    # Campos adicionais usados somente para validação (não estão no modelo)
    bi = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Número do BI (se não tiver Recenseamento preenchido)"
        })
    )

    data_nascimento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control"
        })
    )

    class Meta:
        model = Documento
        fields = ["tipo", "destino", "finalidade"]

        widgets = {
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "destino": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Destino do documento (ex.: Escola, Empresa...)"
            }),
            "finalidade": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Finalidade (ex.: Matrícula, Admissão, Processo...)"
            }),
        }

    # -------------------------------------------------------------------
    # VALIDAÇÕES SIMPLES → Regras complexas ficam no View (como no seu código)
    # -------------------------------------------------------------------

    def clean_tipo(self):
        tipo = self.cleaned_data.get("tipo")

        if tipo not in ["declaracao_militar", "cedula_militar", "recibo_recenseamento"]:
            raise forms.ValidationError("Tipo de documento inválido.")

        return tipo

    def clean(self):
        cleaned = super().clean()

        tipo = cleaned.get("tipo")
        destino = cleaned.get("destino")
        finalidade = cleaned.get("finalidade")

        # Destino é obrigatório para Declaração Militar
        if tipo == "declaracao_militar":
            if not destino:
                self.add_error("destino", "Informe o destino da declaração.")
            if not finalidade:
                self.add_error("finalidade", "Informe a finalidade da declaração.")

        return cleaned
