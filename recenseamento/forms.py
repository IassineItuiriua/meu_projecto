from django import forms
from django.core.exceptions import ValidationError
from datetime import date

from recenseamento.utils.ocr import extrair_numero_bi
from recenseamento.utils.bi import extrair_numero_bi
from .models import Recenseamento, PerfilCidadao
from PIL import Image
from pdf2image import convert_from_path
import pytesseract
from deepface import DeepFace
import unicodedata
import re
import os
from .utils.files import salvar_temp_upload



# Configuração do executável do Tesseract OCR (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# =========================
# FORM RECENSEAMENTO
# =========================
def normalizar_texto(texto):
    if not texto:
        return ""

    # Remove acentos
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ASCII", "ignore").decode("ASCII")

    # Maiúsculas
    texto = texto.upper()

    # Remove caracteres estranhos
    texto = re.sub(r"[^A-Z\s]", " ", texto)

    # Remove espaços duplicados
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto

def normalizar_texto_ocr(texto):
    texto = texto.upper()
    texto = texto.replace("O", "0").replace("I", "1").replace("L", "1")
    texto = re.sub(r"[^A-Z0-9]", "", texto)
    return texto

class RecenseamentoForm(forms.ModelForm):
    class Meta:
        model = Recenseamento
        exclude = ("usuario", "nim", "foi_submetido_exame", "resultado_exame")
        widgets = {
            "nome_completo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome conforme BI"}),
            "data_nascimento": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "filiacao_pai": forms.TextInput(attrs={"class": "form-control"}),
            "filiacao_mae": forms.TextInput(attrs={"class": "form-control"}),
            "nacionalidade": forms.TextInput(attrs={"class": "form-control"}),
            "naturalidade": forms.TextInput(attrs={"class": "form-control"}),
            "morada": forms.TextInput(attrs={"class": "form-control"}),
            "contacto_familiar": forms.TextInput(attrs={"class": "form-control"}),
            "documento_identidade": forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".pdf,.jpg,.jpeg,.png"}),
            "foto_capturada": forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".jpg,.jpeg,.png"}),
        }

    def clean_data_nascimento(self):
        data = self.cleaned_data.get("data_nascimento")
        hoje = date.today()
        idade = hoje.year - data.year - ((hoje.month, hoje.day) < (data.month, data.day))
        if idade < 18 or idade > 35:
            raise ValidationError("A idade permitida para o recenseamento é entre 18 e 35 anos.")
        self.cleaned_data["idade"] = idade
        return data

    def extrair_texto_do_bi(self, bi_file):
        if hasattr(bi_file, 'path'):
            caminho = bi_file.path
        elif hasattr(bi_file, 'temporary_file_path'):
            caminho = bi_file.temporary_file_path()
        elif isinstance(bi_file, str):
            caminho = bi_file
        else:
            raise ValidationError("Arquivo do BI inválido.")

        if caminho.lower().endswith(".pdf"):
            paginas = convert_from_path(caminho)
            texto = ""
            for pagina in paginas:
                texto += pytesseract.image_to_string(pagina)
        else:
            img = Image.open(caminho)
            texto = pytesseract.image_to_string(img)
        return texto

    def extrair_numero_bi(texto):
        texto = normalizar_texto_ocr(texto)

        # padrão comum: 11–13 dígitos + letra final
        match = re.search(r"\d{11,13}[A-Z]", texto)
        if match:
            return match.group()

        # fallback: só números longos
        match = re.search(r"\d{11,13}", texto)
        if match:
            return match.group()

        return None

    def clean(self):
        cleaned_data = super().clean()
        nome_form = cleaned_data.get("nome_completo")
        bi_file = cleaned_data.get("documento_identidade")
        foto_user = cleaned_data.get("foto_capturada")

        bi_path = None
        foto_path = None

        try:
            # Validar nome e extrair BI
            if bi_file and nome_form:
                # Salvar temporariamente se for UploadedFile
                if hasattr(bi_file, 'name'):
                    bi_path = salvar_temp_upload(bi_file)
                elif isinstance(bi_file, str):
                    bi_path = bi_file
                else:
                    raise ValidationError("Arquivo do BI inválido.")

                texto_bi = self.extrair_texto_do_bi(bi_path)

                # Extrair número do BI via regex (13 dígitos)
                numero_bi = extrair_numero_bi(texto_bi)
                if numero_bi:
                    cleaned_data["bi"] = numero_bi
                else:
                    raise ValidationError(
                        "Não foi possível identificar o número do BI. "
                        "Certifique-se de que o documento está legível."
                    )


                # Normalizar e validar nome
                nome_normalizado = normalizar_texto(nome_form)
                texto_normalizado = normalizar_texto(texto_bi)
                if nome_normalizado not in texto_normalizado:
                    raise ValidationError("O nome informado não coincide com o documento de identidade.")

            # Validar foto com DeepFace
            if bi_file and foto_user:
                if not bi_path:
                    if hasattr(bi_file, 'name'):
                        bi_path = salvar_temp_upload(bi_file)
                    elif isinstance(bi_file, str):
                        bi_path = bi_file
                    else:
                        raise ValidationError("Arquivo do BI inválido.")

                if hasattr(foto_user, 'name'):
                    foto_path = salvar_temp_upload(foto_user)
                elif isinstance(foto_user, str):
                    foto_path = foto_user
                else:
                    raise ValidationError("Arquivo da foto inválido.")

                resultado = DeepFace.verify(
                    img1_path=foto_path,
                    img2_path=bi_path,
                    model_name="ArcFace",
                    enforce_detection=False
                )

                if not resultado.get("verified"):
                    raise ValidationError("A foto do documento não coincide com a foto capturada.")

        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Erro ao validar identidade: {str(e)}")
        finally:
            if bi_path and hasattr(bi_file, 'name') and os.path.exists(bi_path):
                os.remove(bi_path)
            if foto_path and hasattr(foto_user, 'name') and os.path.exists(foto_path):
                os.remove(foto_path)

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Atualiza o campo bi com o valor extraído no clean()
        if "bi" in self.cleaned_data:
            instance.bi = self.cleaned_data["bi"]
        if commit:
            instance.save()
        return instance





# =========================
# FORM COMPLETAR PERFIL CIDADÃO
# =========================
class CompletarPerfilCidadaoForm(forms.ModelForm):
    class Meta:
        model = PerfilCidadao
        fields = ("nome_completo", "data_nascimento", "numero_bi", "bi", "foto", "telefone", "email", "dados_confirmados")
        widgets = {
            "nome_completo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome completo conforme BI"}),
            "data_nascimento": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "numero_bi": forms.TextInput(attrs={"class": "form-control", "placeholder": "Número do BI"}),
            "bi": forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".pdf,.jpg,.jpeg,.png"}),
            "foto": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "telefone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Telefone"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
            "dados_confirmados": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_data_nascimento(self):
        data = self.cleaned_data.get("data_nascimento")
        if not data:
            raise ValidationError("Data de nascimento é obrigatória.")
        hoje = date.today()
        idade = hoje.year - data.year - ((hoje.month, hoje.day) < (data.month, data.day))
        if idade < 18:
            raise ValidationError("Idade mínima é 18 anos.")
        self.cleaned_data["idade"] = idade
        return data

    def extrair_texto_do_bi(self, bi_file):
        if hasattr(bi_file, 'path'):
            caminho = bi_file.path
        elif hasattr(bi_file, 'temporary_file_path'):
            caminho = bi_file.temporary_file_path()
        elif isinstance(bi_file, str):
            caminho = bi_file
        else:
            raise ValidationError("Arquivo do BI inválido.")

        if caminho.lower().endswith(".pdf"):
            paginas = convert_from_path(caminho)
            texto = ""
            for pagina in paginas:
                texto += pytesseract.image_to_string(pagina)
        else:
            img = Image.open(caminho)
            texto = pytesseract.image_to_string(img)
        return texto

    def clean(self):
        cleaned_data = super().clean()
        nome_form = cleaned_data.get("nome_completo")
        bi_file = cleaned_data.get("bi")
        foto_user = cleaned_data.get("foto")

        bi_path = None
        foto_path = None

        try:
            if bi_file and nome_form:
                if hasattr(bi_file, 'name'):
                    bi_path = salvar_temp_upload(bi_file)
                elif isinstance(bi_file, str):
                    bi_path = bi_file
                else:
                    raise ValidationError("Arquivo do BI inválido.")

                texto_bi = self.extrair_texto_do_bi(bi_path)

                # Extrair número do BI (13 dígitos)
                numero_bi = extrair_numero_bi(texto_bi)
                if numero_bi:
                    cleaned_data["numero_bi"] = numero_bi  # ✅ Corrigido
                else:
                    raise ValidationError(
                        "Não foi possível extrair o número do BI do documento. "
                        "Certifique-se de que a imagem está legível."
                    )

                # Validar nome
                nome_normalizado = normalizar_texto(nome_form)
                texto_normalizado = normalizar_texto(texto_bi)
                if nome_normalizado not in texto_normalizado:
                    raise ValidationError("O nome informado não coincide com o documento de identidade.")

            # Validar foto
            if bi_file and foto_user:
                if not bi_path:
                    bi_path = salvar_temp_upload(bi_file) if hasattr(bi_file, 'name') else bi_file
                foto_path = salvar_temp_upload(foto_user) if hasattr(foto_user, 'name') else foto_user

                resultado = DeepFace.verify(
                    img1_path=foto_path,
                    img2_path=bi_path,
                    model_name="ArcFace",
                    enforce_detection=False
                )
                if not resultado.get("verified"):
                    raise ValidationError("A foto do documento não coincide com a foto enviada.")

        finally:
            if bi_path and hasattr(bi_file, 'name') and os.path.exists(bi_path):
                os.remove(bi_path)
            if foto_path and hasattr(foto_user, 'name') and os.path.exists(foto_path):
                os.remove(foto_path)

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        numero_bi_extraido = self.cleaned_data.get("numero_bi")  # ✅ Aqui pega o valor correto
        if numero_bi_extraido:
            instance.numero_bi = numero_bi_extraido
        if commit:
            instance.save()
        return instance