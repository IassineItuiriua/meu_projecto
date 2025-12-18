from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Recenseamento, gerar_nim
from .forms import RecenseamentoForm

class RecenseamentoView(LoginRequiredMixin, View):
    template_name = "recenseamento/recensear.html"

    def get(self, request):
        recenseamento = Recenseamento.objects.filter(usuario=request.user).first()
        form = RecenseamentoForm(instance=recenseamento)
        return render(request, self.template_name, {"form": form, "recenseamento": recenseamento})

    def post(self, request):
        recenseamento = Recenseamento.objects.filter(usuario=request.user).first()
        form = RecenseamentoForm(request.POST, request.FILES, instance=recenseamento)

        if form.is_valid():
            rec = form.save(commit=False)
            rec.usuario = request.user
            if not rec.nim:
                rec.nim = gerar_nim()
            rec.save()
            messages.success(request, "Recenseamento guardado com sucesso.")
            return redirect("usuarios:painel")

        return render(request, self.template_name, {"form": form, "recenseamento": recenseamento})
