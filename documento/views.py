from django.shortcuts import get_object_or_404, render, redirect 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .forms import DocumentoForm
from .models import Documento
from recenseamento.models import Recenseamento
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm
from django.conf import settings
import os

# -------------------------------
# Página de visualização de documento
# -------------------------------
@login_required
def visualizar_documento(request, documento_id):
    documento = get_object_or_404(Documento, id=documento_id)

    if documento.usuario != request.user:
        return render(request, "403.html", status=403)

    return render(request, 'documento/visualizar.html', {'documento': documento})

# -------------------------------
# Página para gerar documento
# -------------------------------
@login_required
def gerar_documento(request, documento_id):
    documento = get_object_or_404(Documento, id=documento_id)

    if documento.usuario != request.user:
        return render(request, "403.html", status=403)

    return render(request, 'documento/gerar_documento.html', {'documento': documento})

# -------------------------------
# Solicitar documento
# -------------------------------
@login_required
def solicitar_documento(request):
    if request.method == 'POST':
        form = DocumentoForm(request.POST)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.usuario = request.user

            # Número sequencial automático
            ultimo = Documento.objects.filter(tipo=doc.tipo).order_by('-numero_sequencial').first()
            doc.numero_sequencial = 1 if not ultimo else ultimo.numero_sequencial + 1
            doc.save()

            messages.success(request, "Documento solicitado com sucesso!")
            return redirect('visualizar_documento', documento_id=doc.id)
    else:
        form = DocumentoForm()

    return render(request, 'documento/solicitar_documento.html', {'form': form})

# -------------------------------
# Gerar PDF do documento
# -------------------------------
@login_required
def gerar_pdf_documento(request, documento_id):
    documento = get_object_or_404(Documento, id=documento_id)

    # 🔒 Segurança: só o dono pode gerar PDF
    if documento.usuario != request.user:
        return render(request, "403.html", status=403)

    usuario = request.user

    # 🔒 Verificar se o usuário está recenseado
    try:
        rec = Recenseamento.objects.get(usuario=usuario)
    except Recenseamento.DoesNotExist:
        return HttpResponse("Usuário ainda não está recenseado.", status=400)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{documento.get_tipo_display()}_{documento.numero_sequencial}.pdf"'

    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_normal.fontName = "Helvetica"
    style_normal.fontSize = 12

    style_center = ParagraphStyle(
        'centered',
        parent=style_normal,
        alignment=TA_CENTER,
        fontSize=14,
        spaceAfter=12
    )

    style_title = ParagraphStyle(
        'title',
        parent=style_normal,
        alignment=TA_CENTER,
        fontSize=16,
        spaceAfter=20,
        leading=20,
        spaceBefore=10
    )

    doc_pdf = SimpleDocTemplate(response, pagesize=A4,
                                rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm)
    story = []

    # -------------------------------
    # Inserir imagem no topo do PDF
    # -------------------------------
    imagem_path = os.path.join(settings.BASE_DIR, "static", "meu_projecto", "images", "emblema.jpg")
    if os.path.exists(imagem_path):
        img = Image(imagem_path, width=80, height=80)
        img.hAlign = 'CENTER'
        story.append(img)
        story.append(Spacer(1, 12))

    # -------------------------------
    # Cabeçalho oficial
    # -------------------------------
    cabecalho = (
        "<b>REPÚBLICA DE MOÇAMBIQUE</b><br/>"
        "MINISTÉRIO DA DEFESA NACIONAL<br/>"
        "DIRECÇÃO NACIONAL DE ADMINISTRAÇÃO<br/>"
        "CENTRO PROVINCIAL DE RECRUTAMENTO E MOBILIZAÇÃO"
    )
    story.append(Paragraph(cabecalho, style_center))
    story.append(Spacer(1, 12))

    # -------------------------------
    # Título do documento
    # -------------------------------
    titulo = f"<b>{documento.get_tipo_display()}</b>"
    story.append(Paragraph(titulo, style_title))
    story.append(Spacer(1, 12))

    # -------------------------------
    # Texto do documento
    # -------------------------------
    if documento.tipo == 'declaracao_militar':
        texto = f"""
        Para os devidos efeitos, declara-se que <b>{usuario.first_name} {usuario.last_name}</b>,
        recenseado sob o NIM <b>{rec.nim}</b>, tem o seu serviço militar regularizado.

        O presente documento destina-se a <b>{documento.destino}</b> para efeitos de <b>{documento.finalidade}</b>.
        """
    else:
        texto = f"Documento: <b>{documento.get_tipo_display()}</b><br/>Nome: <b>{usuario.first_name} {usuario.last_name}</b>"

    story.append(Paragraph(texto, style_normal))
    story.append(Spacer(1, 24))

    # -------------------------------
    # Assinatura
    # -------------------------------
    assinatura = """
    <br/><br/><br/>
    ________________________________<br/>
    <b>Diretor do CPRM</b><br/>
    Ministério da Defesa Nacional
    """
    story.append(Paragraph(assinatura, style_center))

    # -------------------------------
    # Gerar PDF
    # -------------------------------
    doc_pdf.build(story)
    return response

# -------------------------------
# Página 403 personalizada
# -------------------------------
def erro_403(request, exception=None):
    return render(request, "403.html", status=403)
