from django.urls import path
from . import views
import usuarios

app_name = 'usuarios'
urlpatterns = [
    path('login/', usuarios.views.login_view, name='login'),
    path('cadastro/', usuarios.views.cadastro, name='cadastro'),
    path('painel/', usuarios.views.painel, name='painel'),
    path('logout/', usuarios.views.logout_view, name='logout'),
]