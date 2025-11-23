# documento/admin.py
from django.contrib import admin
from .models import Documento

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'tipo', 'finalidade', 'numero_sequencial', 'criado_em')
    search_fields = ('usuario__username', 'finalidade', 'destino')
    list_filter = ('tipo', 'criado_em')
    ordering = ('-criado_em',)
    list_per_page = 20
