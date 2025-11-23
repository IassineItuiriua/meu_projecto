from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Documento(models.Model):
    TIPO_DOCUMENTO = [
        ('declaracao_militar', 'Declaração Militar'),
        ('cedula_militar', 'Cédula Militar'),
        ('recibo_recenseamento', 'Recibo de Recenseamento Militar'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    tipo = models.CharField(max_length=50, choices=TIPO_DOCUMENTO)
    destino = models.CharField(max_length=200, blank=True, null=True)
    finalidade = models.CharField(max_length=200, blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    numero_sequencial = models.PositiveIntegerField()

    class Meta:
        ordering = ['-criado_em']
        #unique_together = ('usuario', 'numero_sequencial')

    def save(self, *args, **kwargs):
        # Gera o número sequencial APENAS na criação
        if not self.pk:  # Só gera no primeiro save
            if self.usuario:
                ultimo = (
                    Documento.objects
                    .filter(usuario=self.usuario)
                    .order_by('-numero_sequencial')
                    .first()
                )
                if ultimo:
                    self.numero_sequencial = ultimo.numero_sequencial + 1
                else:
                    self.numero_sequencial = 1
            else:
                # fallback — evita erros ao migrar dados antigos
                self.numero_sequencial = 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.usuario} - #{self.numero_sequencial}"
