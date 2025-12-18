# documento/mixins.py
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

class DocumentoOwnerMixin(UserPassesTestMixin):
    """
    Garante que apenas o dono do documento pode aceder.
    Usar em Class-Based Views que trabalham com um objecto (DetailView, UpdateView, etc).
    """
    raise_exception = False  # vamos tratar retornando template 403

    def handle_no_permission(self):
        # retorna o template 403 (você comentou ter um template project-level 403.html)
        return render(self.request, "403.html", status=403)

    def test_func(self):
        obj = None
        # tenta obter objecto com a API habitual do CBV
        try:
            obj = self.get_object()
        except Exception:
            # se não for possível obter objecto aqui, negar
            return False
        return obj.usuario == self.request.user
