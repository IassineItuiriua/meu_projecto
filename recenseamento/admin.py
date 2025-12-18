from django.contrib import admin
from .models import Recenseamento, PerfilCidadao


@admin.register(Recenseamento)
class RecenseamentoAdmin(admin.ModelAdmin):
    list_display = (
        "nome_completo",
        "nim",
        "bi",
        "data_nascimento",
        "telefone",
        "email",
        "foi_submetido_exame",
        "resultado_exame",
    )

    list_filter = (
        "foi_submetido_exame",
        "resultado_exame",
        "data_nascimento",
    )

    search_fields = (
        "nome_completo",
        "nim",
        "bi",
        "telefone",
        "email",
    )

    readonly_fields = ("nim",)

    fieldsets = (
        ("Identificação Militar", {
            "fields": ("nim", "bi")
        }),
        ("Dados Pessoais", {
            "fields": (
                "usuario",
                "nome_completo",
                "data_nascimento",
                "filiacao_pai",
                "filiacao_mae",
                "nacionalidade",
                "naturalidade",
                "morada",
            )
        }),
        ("Contactos", {
            "fields": (
                "telefone",
                "email",
                "contacto_familiar",
            )
        }),
        ("Documentos", {
            "fields": (
                "documento_identidade",
                "foto_capturada",
            )
        }),
        ("Exame Militar", {
            "fields": (
                "foi_submetido_exame",
                "resultado_exame",
            )
        }),
    )

    ordering = ("-id",)


@admin.register(PerfilCidadao)
class PerfilCidadaoAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "nome_completo",
        "numero_bi",
        "telefone",
        "email",
        "dados_confirmados",
    )

    list_filter = ("dados_confirmados",)

    search_fields = (
        "user__username",
        "nome_completo",
        "numero_bi",
        "telefone",
        "email",
    )

    fieldsets = (
        ("Utilizador", {
            "fields": ("user",)
        }),
        ("Identificação", {
            "fields": (
                "nome_completo",
                "numero_bi",
                "data_nascimento",
            )
        }),
        ("Contactos", {
            "fields": (
                "telefone",
                "email",
            )
        }),
        ("Documentos", {
            "fields": (
                "bi",
                "foto",
            )
        }),
        ("Estado", {
            "fields": ("dados_confirmados",)
        }),
    )
