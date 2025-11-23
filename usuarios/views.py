from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from recenseamento.models import Recenseamento
from .forms import UsuarioCreationForm


# === Cadastro ===
def cadastro(request):
    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuarios:login')
    else:
        form = UsuarioCreationForm()

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


# === Painel ===
@login_required
def painel(request):
    try:
        recenseamento = Recenseamento.objects.get(usuario=request.user)
    except Recenseamento.DoesNotExist:
        recenseamento = None

    return render(request, "usuarios/painel.html", {
        "recenseamento": recenseamento
    })
