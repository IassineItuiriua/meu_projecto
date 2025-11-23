from django.contrib import admin
from .models import Recenseamento

@admin.register(Recenseamento)
class RecenseamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'nome_completo', 'nim', 'telefone', 'email', 'tem_documento')
    search_fields = ('nome_completo', 'usuario__username')
    list_filter = ('nacionalidade',)
    ordering = ('nome_completo',)
    list_per_page = 20

    def tem_documento(self, obj):
        return bool(obj.documento_identidade)
    tem_documento.boolean = True
    tem_documento.short_description = "Documento Carregado?"
