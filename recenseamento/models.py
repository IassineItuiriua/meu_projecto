from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from datetime import date, datetime



def gerar_nim():
    ano = datetime.now().year
    ultimo = Recenseamento.objects.filter(nim__isnull=False).exclude(nim='').order_by('-id').first()
    if not ultimo:
        sequencial = 1
    else:
        try:
            sequencial = int(ultimo.nim.split('-')[-1]) + 1
        except:
            sequencial = 1
    return f"FADM-{ano}-{sequencial:06d}"
def upload_foto(instance, filename):
    return f"uploads/fotos/{instance.usuario.id}/{filename}"

def upload_doc(instance, filename):
    return f"uploads/documentos/{instance.usuario.id}/{filename}"

class Recenseamento(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bi = models.CharField(max_length=13, unique=True, null=True, blank=True)
    data_nascimento = models.DateField()
    nim = models.CharField(max_length=20, unique=True, blank=True, null=True)

    nome_completo = models.CharField(max_length=150)
    filiacao_pai = models.CharField(max_length=150)
    filiacao_mae = models.CharField(max_length=150)
    nacionalidade = models.CharField(max_length=100)
    naturalidade = models.CharField(max_length=100)
    morada = models.CharField(max_length=200)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()
    contacto_familiar = models.CharField(max_length=150)

    
    documento_identidade = models.FileField(upload_to='documentos_identidade_uploads/', null=True, blank=True)
    foto_capturada = models.ImageField(upload_to='selfies/', null=True, blank=True)

    foi_submetido_exame = models.BooleanField(null=True, blank=True)
    resultado_exame = models.CharField(
    max_length=10,
    choices=(('apto', 'Apto'), ('inapto', 'Inapto')),
    null=True,
    blank=True
)
    def completo(self):
        campos = [
            self.bi,
            self.data_nascimento,
            self.nome_completo,
            self.filiacao_pai,
            self.filiacao_mae,
            self.nacionalidade,
            self.naturalidade,
            self.morada,
            self.telefone,
            self.email,
            self.contacto_familiar,
            self.documento_identidade,
        ]
        return all(campos)
    
    
        
    def clean(self):
        # verificar se a data existe
        if not self.data_nascimento:
            raise ValidationError("A data de nascimento é obrigatória.")

        # validação de idade
        hoje = date.today()

        idade = (
            hoje.year
            - self.data_nascimento.year
            - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))
        )

        if idade < 18 or idade > 35:
            raise ValidationError("A idade permitida para recenseamento é entre 18 e 35 anos.")

    def __str__(self):
        return f"{self.nome_completo} ({self.nim})"

class PerfilCidadao(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bi = models.FileField(upload_to="documentos/bi/", null=True, blank=True)
    foto = models.ImageField(upload_to="perfil_fotos/", null=True, blank=True)

    dados_confirmados = models.BooleanField(default=False)
    data_nascimento = models.DateField(null=True, blank=True)
    nome_completo = models.CharField(max_length=255, blank=True, null=True)
    numero_bi = models.CharField(max_length=13, unique=True, null=True, blank=True)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()

    def completo(self):
        return bool(self.bi and self.foto and self.dados_confirmados and  self.nome_completo and self.numero_bi and self.telefone and self.email)

    def __str__(self):
        return f"Perfil de {self.user.username}"
    