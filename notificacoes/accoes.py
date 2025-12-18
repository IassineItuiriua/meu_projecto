from django.conf import settings
from notificacoes.email_service import enviar_email

# -----------------------------
# 1 — Após cadastro
# -----------------------------
def apos_registro(user):
    assunto = "Cadastro realizado com sucesso"
    texto = f"Olá {user.first_name}, seu cadastro foi concluído com sucesso."
    html = f"<h2>Olá {user.first_name}!</h2><p>Seu cadastro foi realizado com sucesso 👌</p>"

    enviar_email(user.email, assunto, texto, html)



# -----------------------------
# 2 — Após recenseamento
# -----------------------------
def apos_recenseamento(user, nim):
    assunto = "Recenseamento concluído"
    texto = f"Olá {user.first_name}, seu recenseamento foi concluído com sucesso. NIM: {nim}"
    html = f"<h2>Olá {user.first_name}!</h2><p>Seu recenseamento foi concluído com sucesso.</p><p><b>NIM:</b> {nim}</p>"

    enviar_email(user.email, assunto, texto, html)


# -----------------------------
# 3 — Após emissão de documento
# -----------------------------
def apos_documento_emitido(user, documento):
    tipo_doc = documento.get_tipo_display()
    assunto = "Documento emitido com sucesso"
    texto = f"Olá {user.first_name}, seu documento '{tipo_doc}' foi emitido."
    html = f"<h2>Documento emitido!</h2><p>O documento <b>{tipo_doc}</b> foi emitido com sucesso.</p>"

    enviar_email(user.email, assunto, texto, html)


def apos_completar_perfil(user):
    assunto = "Perfil Atualizado com Sucesso"

    texto = (
        f"Olá {user.first_name}, o seu Perfil de Cidadão foi atualizado com sucesso.\n"
        "Agora já pode solicitar documentos militares através do sistema."
    )

    html = (
        "<h2>Perfil atualizado!</h2>"
        "<p>O seu <b>Perfil de Cidadão (+35 anos)</b> foi atualizado com sucesso.</p>"
        "<p>Agora já pode solicitar documentos militares.</p>"
    )

    enviar_email(user.email, assunto, texto, html)

    # 🔔 SMS (se tiver telefone cadastrado)
    if getattr(user, "telefone", None):
        sms_msg = "Seu Perfil de Cidadão foi atualizado com sucesso."
        enviar_sms(user.telefone, sms_msg)

def apos_documento_emitido_cidadao35(user, documento):
    tipo_doc = documento.get_tipo_display()
    assunto = "Documento emitido com sucesso"

    texto = (
        f"Olá {user.first_name}, o seu documento '{tipo_doc}' foi emitido com sucesso.\n"
        "Pode fazer o download diretamente no sistema."
    )

    html = (
        "<h2>Documento emitido!</h2>"
        f"<p>O documento <b>{tipo_doc}</b> foi emitido com sucesso.</p>"
        "<p>Já está disponível na sua área de utilizador.</p>"
    )

    enviar_email(user.email, assunto, texto, html)

    # 🔔 SMS opcional
    if getattr(user, "telefone", None):
        sms_msg = f"Documento '{tipo_doc}' emitido com sucesso."
        enviar_sms(user.telefone, sms_msg)
