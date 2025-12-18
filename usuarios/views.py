from pyexpat.errors import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from notificacoes.accoes import apos_registro
from recenseamento.forms import CompletarPerfilCidadaoForm, RecenseamentoForm
from recenseamento.models import Recenseamento
from .forms import CompletarPerfilUsuarioForm, UserRegistrationForm
from datetime import date
import tempfile
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from documento.views import calcular_idade #validar_identidade
from notificacoes.accoes import apos_registro
from recenseamento.models import PerfilCidadao, Recenseamento
from documento.utils import extrair_numero_bi
import os

#from .forms import CompletarPerfilCidadaoForm, CompletarPerfilUsuarioForm, CompletarRecenseamentoForm, UserRegistrationForm
from deepface import DeepFace


# === Cadastro ===
def cadastro(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            novo_usuario = form.save()

            # 🔔 Enviar e-mail
            apos_registro(novo_usuario)

            messages.success(request, "Conta criada com sucesso. Faça login.")
            return redirect('usuarios:login')
    else:
        form = UserRegistrationForm()  # ✅ FORM CORRETO

    return render(request, 'usuarios/cadastro.html', {'form': form})




# === Login ===
def login_view(request):
    next_url = request.GET.get('next', '')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        next_url = request.POST.get('next', '')

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Se houver next válido, redireciona para o painel
            if next_url and next_url.startswith('/'):
                return redirect(next_url)

            return redirect('usuarios:painel')

    else:
        form = AuthenticationForm()

    return render(request, 'usuarios/login.html', {
        'form': form,
        'next': next_url
    })



# === Logout ===
def logout_view(request):
    logout(request)
    return redirect('usuarios:login')


# Inicializa o modelo uma única vez para cache
deepface_model_cache = DeepFace.build_model("ArcFace")


@login_required
def completar_perfil(request):
    usuario = request.user

    perfil = PerfilCidadao.objects.filter(user=usuario).first()
    recenseamento = getattr(usuario, 'recenseamento', None)

    # ----------------------------
    # CALCULAR IDADE (SEGURO)
    # ----------------------------
    idade = None
    if recenseamento and recenseamento.data_nascimento:
        idade = (date.today() - recenseamento.data_nascimento).days // 365
    elif perfil and perfil.data_nascimento:
        idade = (date.today() - perfil.data_nascimento).days // 365

    # ----------------------------
    # POST
    # ----------------------------
    if request.method == "POST":
        form_usuario = CompletarPerfilUsuarioForm(request.POST, instance=usuario)
        form_recenseamento = RecenseamentoForm(
            request.POST, request.FILES, instance=recenseamento
        )
        form_cidadao = CompletarPerfilCidadaoForm(
            request.POST, request.FILES, instance=perfil
        )

        def render_forms():
            return render(request, "usuarios/completar_perfil.html", {
                "form_usuario": form_usuario,
                "form_recenseamento": form_recenseamento,
                "form_cidadao": form_cidadao,
                "idade": idade or 0,
            })

        # ----------------------------
        # SALVAR DADOS BÁSICOS
        # ----------------------------
        if not form_usuario.is_valid():
            return render_forms()
        form_usuario.save()

        # ----------------------------
        # CASO 1: IDADE INDEFINIDA
        # ----------------------------
        # ----------------------------
        # GARANTIR DATA DE NASCIMENTO
        # ----------------------------
        if idade is None:
            data_nasc = None

            if form_recenseamento.is_valid():
                data_nasc = form_recenseamento.cleaned_data.get("data_nascimento")

            if not data_nasc and form_cidadao.is_valid():
                data_nasc = form_cidadao.cleaned_data.get("data_nascimento")

            if not data_nasc:
                messages.error(request, "Informe a data de nascimento para continuar.")
                return render_forms()

            idade = (date.today() - data_nasc).days // 365


        # ----------------------------
        # CASO 2: ATÉ 35 ANOS (RECENSEAMENTO)
        # ----------------------------
        if idade <= 35:
            if not form_recenseamento.is_valid():
                return render_forms()

            rec = form_recenseamento.save(commit=False)
            rec.usuario = usuario
            rec.save()

            messages.success(request, "Recenseamento concluído com sucesso!")
            return redirect("usuarios:painel")

        # ----------------------------
        # CASO 3: MAIOR DE 35 (PERFIL CIDADÃO)
        # ----------------------------
        if not form_cidadao.is_valid():
            return render_forms()

        data_nasc = form_cidadao.cleaned_data.get("data_nascimento")
        # 🔐 Arquivos DEVEM vir de request.FILES
        foto = request.FILES.get("foto")
        bi_file = request.FILES.get("bi")


        if not data_nasc:
            messages.error(request, "A data de nascimento é obrigatória.")
            return render_forms()

        if not foto or not bi_file:
            messages.error(
                request,
                "Para maiores de 35 anos é obrigatório enviar foto e BI."
            )
            return render_forms()

        # ----------------------------
        # VALIDAÇÃO FACIAL (SEGURA)
        # ----------------------------
        # ----------------------------
# VALIDAÇÃO FACIAL (SEGURA)
# ----------------------------
        if foto and bi_file:
            try:
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_foto, \
                    tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_bi:

                    for chunk in foto.chunks():
                        tmp_foto.write(chunk)

                    for chunk in bi_file.chunks():
                        tmp_bi.write(chunk)

                    tmp_foto.flush()
                    tmp_bi.flush()

                    resultado = DeepFace.verify(
                        img1_path=tmp_foto.name,
                        img2_path=tmp_bi.name,
                        model_name="ArcFace",
                        distance_metric="cosine",
                        enforce_detection=False,
                    )

                    LIMIAR_FACIAL = 0.55

                    if not resultado.get("verified") or resultado.get("distance", 1) > LIMIAR_FACIAL:
                        messages.error(
                            request,
                            f"Falha na verificação facial (distância: {resultado.get('distance', 0):.3f})"
                        )
                        return render_forms()

            except Exception as e:
                messages.error(request, f"Erro na validação facial: {str(e)}")
                return render_forms()


        # ----------------------------
        # SALVAR PERFIL CIDADÃO
        # ----------------------------
        perfil = form_cidadao.save(commit=False)
        perfil.user = usuario
        perfil.save()

        messages.success(request, "Perfil atualizado com sucesso!")
        return redirect("usuarios:painel")

    # ----------------------------
    # GET
    # ----------------------------
    else:
        form_usuario = CompletarPerfilUsuarioForm(instance=usuario)
        form_recenseamento = RecenseamentoForm(instance=recenseamento)
        form_cidadao = CompletarPerfilCidadaoForm(instance=perfil)

    return render(request, "usuarios/completar_perfil.html", {
        "form_usuario": form_usuario,
        "form_recenseamento": form_recenseamento,
        "form_cidadao": form_cidadao,
        "idade": idade or 0,
    })


@login_required
def painel(request):

    user = request.user

    # Dados do recenseamento (18–35 anos)
    recenseamento = Recenseamento.objects.filter(usuario=user).first()

    # Perfil do cidadão (+35 anos)
    perfil = PerfilCidadao.objects.filter(user=user).first()

    # ----------------------------
    # CALCULAR IDADE
    # ----------------------------
    idade = None
    if recenseamento and recenseamento.data_nascimento:
        idade = calcular_idade(recenseamento.data_nascimento)
    elif perfil and perfil.data_nascimento:
        idade = calcular_idade(perfil.data_nascimento)

    # ----------------------------
    # PERFIL INCOMPLETO (somente para +35 anos)
    # ----------------------------
    perfil_incompleto = False
    if not recenseamento and idade and idade > 35:
        # Para +35 anos: BI + foto + data nascimento + numero_bi
        campos = [
            perfil.bi,
            perfil.foto,
            perfil.data_nascimento,
            perfil.numero_bi,
        ]
        if not all(campos):
            perfil_incompleto = True

    contexto = {
        "recenseamento": recenseamento,   # se existe → 18–35
        "perfil_incompleto": perfil_incompleto,  # apenas para +35
        "perfil": perfil,
    }

    return render(request, "usuarios/painel.html", contexto)


# @login_required
# def painel(request):
#     user = request.user

#     # Pega recenseamento e perfil cidadão
#     rec = Recenseamento.objects.filter(usuario=user).first()
#     perfil = PerfilCidadao.objects.filter(user=user).first()

#     idade = calcular_idade(
#         rec.data_nascimento if rec else perfil.data_nascimento if perfil else None
#     )

#     return render(request, "usuarios/painel.html", {
#         "user": user,
#         "recenseamento": rec,
#         "perfil": perfil,
#         "idade": idade,
#     })
