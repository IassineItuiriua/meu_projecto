from django.core.mail import send_mail
from django.conf import settings

def enviar_email(destinatario, assunto, mensagem_simples, mensagem_html=None):
    """
    Serviço genérico para envio de e-mails.
    Pode ser usado por qualquer app do sistema.
    """

    try:
        send_mail(
            subject=assunto,
            message=mensagem_simples,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinatario],
            html_message=mensagem_html,
            fail_silently=False
        )
        print(f"✅ Email enviado para {destinatario}")
        return True
    except Exception as e:
        print("=== ERRO AO ENVIAR EMAIL ===")
        print(e)
        print("============================")
        return False

