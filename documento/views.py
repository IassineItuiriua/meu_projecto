from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse
from datetime import date
import os
from documento.mixins import DocumentoOwnerMixin
from notificacoes.accoes import apos_documento_emitido
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm
from django.conf import settings
from .forms import SolicitarDocumentoForm
from .models import Documento
from recenseamento.models import Recenseamento, PerfilCidadao
from django.conf import settings


# -----------------------------------------
# UTILITÁRIO: cálculo de idade
# -----------------------------------------
def calcular_idade(data_nasc):
    if not data_nasc:
        return None
    hoje = date.today()
    return hoje.year - data_nasc.year - (
        (hoje.month, hoje.day) < (data_nasc.month, data_nasc.day)
    )


# ==============================================================
# 1) SOLICITAR DOCUMENTO
# ==============================================================
class SolicitarDocumentoView(LoginRequiredMixin, FormView):
    template_name = "documento/solicitar_documento.html"
    form_class = SolicitarDocumentoForm

    def form_valid(self, form):
        user = self.request.user
        tipo_doc = form.cleaned_data["tipo"]
        destino = form.cleaned_data.get("destino")
        finalidade = form.cleaned_data.get("finalidade")
        bi_input = form.cleaned_data.get("bi")
        data_nasc_input = form.cleaned_data.get("data_nascimento")

        # MODELOS CORRETOS
        perfil = PerfilCidadao.objects.filter(user=user).first()
        rec = Recenseamento.objects.filter(usuario=user).first()

        # CALCULAR IDADE
        if rec and rec.data_nascimento:
            idade = calcular_idade(rec.data_nascimento)
        elif perfil and perfil.data_nascimento:
            idade = calcular_idade(perfil.data_nascimento)
        elif data_nasc_input:
            idade = calcular_idade(data_nasc_input)
        else:
            messages.error(self.request, "Data de nascimento inválida ou ausente.")
            return self.render_to_response(self.get_context_data(form=form))

        # ----------------------------------------------------------------------
        #  FLUXO PARA +35 ANOS (SOMENTE PERFILCIDADAO)
        # ----------------------------------------------------------------------
        if idade >= 35:

            # Bloquear qualquer documento diferente de "declaracao"
            if tipo_doc != "declaracao_militar":
                messages.error(self.request, "Usuários com mais de 35 anos só podem solicitar Declaração Militar.")
                return self.render_to_response(self.get_context_data(form=form))

            if not perfil:
                messages.error(self.request, "Complete o Perfil do Cidadão antes de solicitar documentos.")
                return self.render_to_response(self.get_context_data(form=form))

            if not perfil.bi or not perfil.foto:
                messages.error(self.request, "É necessário enviar o BI e a Fotografia no Perfil do Cidadão.")
                return self.render_to_response(self.get_context_data(form=form))

            # Criar documento numerado
            ultimo = Documento.objects.filter(usuario=user).order_by('-numero_sequencial').first()
            numero = 1 if not ultimo else ultimo.numero_sequencial + 1

            doc = Documento.objects.create(
                usuario=user,
                tipo=tipo_doc,
                destino=destino,
                finalidade=finalidade,
                numero_sequencial=numero
            )
            # 🔔 Notificação automática
            apos_documento_emitido(user, doc)
            messages.success(self.request, "Documento criado com sucesso.")
            return redirect("documento:visualizar_documento", documento_id=doc.id)

        # ----------------------------------------------------------------------
        #  FLUXO PARA 18–35 ANOS (RECENSEAMENTO OBRIGATÓRIO)
        # ----------------------------------------------------------------------
        if not rec:
            # Permitir verificação manual com BI e data
            if bi_input and data_nasc_input:
                try:
                    rec_found = Recenseamento.objects.get(bi=bi_input, data_nascimento=data_nasc_input)
                except Recenseamento.DoesNotExist:
                    messages.error(self.request, "Dados não encontrados no Recenseamento Militar.")
                    return self.render_to_response(self.get_context_data(form=form))

                if rec_found.usuario != user:
                    messages.error(self.request, "Os dados informados pertencem a outro usuário.")
                    return self.render_to_response(self.get_context_data(form=form))

                rec = rec_found
            else:
                messages.error(self.request, "Complete o Recenseamento Militar antes de solicitar documentos.")
                return self.render_to_response(self.get_context_data(form=form))

        # Recalcular idade com recenseamento
        idade = calcular_idade(rec.data_nascimento)

        # ----------------------------- CONTROLO DO EXAME PARA CÉDULA -------------------------
        if tipo_doc == "cedula_militar":

            if rec.foi_submetido_exame is None:
                return redirect("documento:confirmar_exame", pessoa_id=rec.id)

            if rec.foi_submetido_exame and rec.resultado_exame == "pendente":
                return render(self.request, "documento/pendente_admin.html", {
                    "mensagem": "O exame foi submetido e aguarda validação do Administrador."
                })

            if rec.foi_submetido_exame is False:
                return render(self.request, "documento/erro_exame.html", {
                    "mensagem": "Para solicitar a Cédula Militar deve submeter o Exame Médico."
                })

            if rec.resultado_exame not in ["apto", "inapto"]:
                return render(self.request, "documento/pendente_admin.html", {
                    "mensagem": "Exame submetido. Aguarde a validação."
                })

        # ----------------------------- CRIAR DOCUMENTO PARA 18-35 -----------------------------
        ultimo = Documento.objects.filter(usuario=user).order_by('-numero_sequencial').first()
        numero = 1 if not ultimo else ultimo.numero_sequencial + 1

        doc = Documento.objects.create(
            usuario=user,
            tipo=tipo_doc,
            destino=destino,
            finalidade=finalidade,
            numero_sequencial=numero
        )

        messages.success(self.request, "Documento criado com sucesso.")
        return redirect("documento:visualizar_documento", documento_id=doc.id)



# ==============================================================
# 2) VISUALIZAR DOCUMENTO
# ==============================================================
class VisualizarDocumentoView(LoginRequiredMixin, DocumentoOwnerMixin, DetailView):
    model = Documento
    template_name = "documento/visualizar.html"
    pk_url_kwarg = "documento_id"
    context_object_name = "documento"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        rec = Recenseamento.objects.filter(usuario=user).first()
        perfil = PerfilCidadao.objects.filter(user=user).first()

        idade = None
        if rec:
            idade = calcular_idade(rec.data_nascimento)
        elif perfil:
            idade = calcular_idade(perfil.data_nascimento)

        if idade is not None and idade <= 35 and rec:
            dados = {
                "nome_completo": rec.nome_completo,
                "bi": rec.bi,  # recenseamento já tem bi como CharField
                "nim": rec.nim,
            }
        elif idade is not None and idade > 35 and perfil:
            dados = {
                "nome_completo": perfil.nome_completo or user.get_full_name(),
                "bi": perfil.numero_bi or "N/A",  # usa numero_bi do PerfilCidadao
                "nim": "N/A",
            }
        else:
            dados = {
                "nome_completo": user.get_full_name(),
                "bi": "N/A",
                "nim": "N/A",
            }

        ctx["dados_usuario"] = dados
        ctx["idade"] = idade
        return ctx


# ==============================================================
# 3) TELA GERAR DOCUMENTO (botão para baixar PDF)
# ==============================================================
class GerarDocumentoView(LoginRequiredMixin, DocumentoOwnerMixin,  DetailView):
    model = Documento
    template_name = "documento/gerar_documento.html"
    pk_url_kwarg = "documento_id"
    context_object_name = "documento"


# ==============================================================
# 4) CONFIRMAR EXAME MÉDICO
# ==============================================================
class ConfirmarExameView(LoginRequiredMixin, View):

    def get(self, request, pessoa_id):
        pessoa = get_object_or_404(Recenseamento, id=pessoa_id)
        if pessoa.usuario != request.user:
            return render(request, "403.html", status=403)
        return render(request, "documento/confirmar_exame.html", {"pessoa": pessoa})

    def post(self, request, pessoa_id):
        pessoa = get_object_or_404(Recenseamento, id=pessoa_id)

        if pessoa.usuario != request.user:
            return render(request, "403.html", status=403)

        resposta = request.POST.get("resposta")

        if resposta == "sim":
            pessoa.foi_submetido_exame = True
            pessoa.resultado_exame = "pendente"
            pessoa.save()
            return render(request, "documento/pendente_admin.html", {
                "mensagem": "Aguarde. O Administrador validará o resultado do Exame Médico."
            })

        pessoa.foi_submetido_exame = False
        pessoa.save()
        return render(request, "documento/erro_exame.html", {
            "mensagem": "Não pode solicitar Cédula Militar sem Exame Médico."
        })


# ==============================================================
# 5) GERAR E BAIXAR PDF
# ==============================================================
class BaixarPDFDocumentoView(LoginRequiredMixin, View):

    def get(self, request, documento_id):
        documento = get_object_or_404(Documento, id=documento_id)
        user = request.user

        if documento.usuario != user:
            return render(request, "403.html", status=403)

        rec = Recenseamento.objects.filter(usuario=user).first()
        perfil = PerfilCidadao.objects.filter(user=user).first()

        # -------------------
        # Seleção correta do BI
        # -------------------
        if rec and calcular_idade(rec.data_nascimento) <= 35:
            nome = rec.nome_completo
            bi = rec.bi or "N/A"
            data_nasc = rec.data_nascimento
            nim = rec.nim or "N/A"
            resultado_exame = rec.resultado_exame
        elif perfil:
            nome = perfil.nome_completo or user.get_full_name()
            bi = perfil.numero_bi or "N/A"  # Aqui pegamos numero_bi do PerfilCidadao
            data_nasc = perfil.data_nascimento
            nim = "N/A"
            resultado_exame = None
        else:
            return HttpResponse("Dados do cidadão não encontrados.", status=400)

        # -------------------
        # Geração do PDF
        # -------------------
        response = HttpResponse(content_type='application/pdf')
        filename = f"{documento.get_tipo_display()}_{documento.numero_sequencial}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        styles = getSampleStyleSheet()
        normal = styles["Normal"]
        normal.fontName = "Helvetica"
        normal.fontSize = 12
        center = ParagraphStyle("centered", parent=normal, alignment=TA_CENTER, fontSize=14)
        title = ParagraphStyle("title", parent=normal, alignment=TA_CENTER, fontSize=16, spaceBefore=15, spaceAfter=15)

        doc_pdf = SimpleDocTemplate(response, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm)
        story = []

        # Logo
        img_path = os.path.join(settings.BASE_DIR, "static", "meu_projecto", "images", "emblema.jpg")
        if os.path.exists(img_path):
            logo = Image(img_path, width=80, height=80)
            logo.hAlign = "CENTER"
            story.append(logo)
            story.append(Spacer(1, 12))

        cabecalho = (
            "<b>REPÚBLICA DE MOÇAMBIQUE</b><br/>"
            "MINISTÉRIO DA DEFESA NACIONAL<br/>"
            "DIRECÇÃO NACIONAL DE ADMINISTRAÇÃO<br/>"
            "CENTRO PROVINCIAL DE RECRUTAMENTO E MOBILIZAÇÃO"
        )
        story.append(Paragraph(cabecalho, center))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"<b>{documento.get_tipo_display()}</b>", title))

        # Texto do documento
        if documento.tipo == "declaracao_militar":
            texto = f"""
            Para os devidos efeitos, declara-se que <b>{nome}</b>, portador do BI <b>{bi}</b>
            e identificado sob o NIM <b>{nim}</b>, encontra-se com o seu Serviço Militar
            regularizado.<br/><br/>
            O presente documento destina-se a <b>{documento.destino}</b> para efeitos de <b>{documento.finalidade}</b>.
            """
        elif documento.tipo == "recibo_recenseamento":
            texto = f"""
            Nome: <b>{nome}</b><br/>
            Data de nascimento: <b>{data_nasc}</b><br/>
            BI: <b>{bi}</b><br/>
            NIM: <b>{nim}</b><br/><br/>
            O presente documento comprova que o cidadão acima identificado realizou o Recenseamento Militar.
            """
        elif documento.tipo == "cedula_militar":
            resultado = (resultado_exame or "NÃO DEFINIDO").upper()
            texto = f"""
            Nome: <b>{nome}</b><br/>
            Data de nascimento: <b>{data_nasc}</b><br/>
            BI: <b>{bi}</b><br/>
            NIM: <b>{nim}</b><br/><br/>
            <b>Resultado dos Exames Médicos:</b> {resultado}<br/><br/>
            Após avaliação médica, o cidadão acima identificado foi classificado como:
            <b>{resultado}</b> para efeitos do cumprimento do Serviço Militar Obrigatório.
            """
        else:
            texto = "Documento não reconhecido pelo sistema."

        story.append(Paragraph(texto, normal))
        story.append(Spacer(1, 25))

        assinatura = """
        ________________________________<br/>
        <b>Diretor do CPRM</b><br/>
        Ministério da Defesa Nacional
        """
        story.append(Paragraph(assinatura, center))

        doc_pdf.build(story)
        return response

