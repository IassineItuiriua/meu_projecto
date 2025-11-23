from django.db import models
from usuarios.models import CustomUser
from datetime import datetime

def gerar_nim():
    ano = datetime.now().year

    # Buscar último sequencial válido
    ultimo = Recenseamento.objects.filter(nim__isnull=False).exclude(nim='').order_by('-id').first()

    if not ultimo:
        sequencial = 1
    else:
        try:
            sequencial = int(ultimo.nim.split('-')[-1]) + 1
        except:
            sequencial = 1

    return f"FADM-{ano}-{sequencial:06d}"


class Recenseamento(models.Model):
    usuario = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    nim = models.CharField(max_length=20, unique=True, blank=True, null=True)

    nome_completo = models.CharField(max_length=150)
    filiacao_pai = models.CharField(max_length=150)
    filiacao_mae = models.CharField(max_length=150)
    data_nascimento = models.DateField()
    nacionalidade = models.CharField(max_length=100)
    naturalidade = models.CharField(max_length=100)
    morada = models.CharField(max_length=200)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()
    contacto_familiar = models.CharField(max_length=150)
    documento_identidade = models.FileField(upload_to='documentos_identidade/')

    def __str__(self):
        return f"{self.nome_completo} ({self.nim})"

