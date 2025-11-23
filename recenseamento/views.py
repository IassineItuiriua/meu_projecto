from datetime import date
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Recenseamento, gerar_nim
from .forms import RecenseamentoForm
from django.http import HttpResponse
from reportlab.pdfgen import canvas

@login_required
def recenseamento(request):
    usuario = request.user

    # Se já existe recenseamento → bloquear
    if Recenseamento.objects.filter(usuario=usuario).exists():
        messages.error(request, "Você já está recenseado.")
        return redirect("usuarios:painel")

    if request.method == "POST":
        form = RecenseamentoForm(request.POST, request.FILES)
        if form.is_valid():

            # validar idade
            data_nasc = form.cleaned_data['data_nascimento']
            idade = (date.today() - data_nasc).days // 365
            if idade < 18 or idade > 35:
                messages.error(request, "A idade permitida para recenseamento é entre 18 e 35 anos.")
                return render(request, "recenseamento/recensear.html", {"form": form})

            rec = form.save(commit=False)
            rec.usuario = usuario

            # --- Gerar NIM corretamente ---
            rec.nim = gerar_nim()
            rec.save()

            # Opcional: salvar também no user
            usuario.nim = rec.nim
            usuario.save()

            messages.success(request, "Recenseamento concluído com sucesso!")
            return redirect("usuarios:painel")

    else:
        form = RecenseamentoForm()

    return render(request, "recenseamento/recensear.html", {"form": form})


@login_required
def painel(request):
    try:
        recenseamento = Recenseamento.objects.get(usuario=request.user)
    except Recenseamento.DoesNotExist:
        recenseamento = None

    return render(request, 'usuarios/painel.html', {
        "recenseamento": recenseamento
    })