from django.urls import path
from . import views
app_name = "recenseamento"
urlpatterns = [
    #path('painel/', views.recenseamento, name='painel'),
    # path('gerar_documento/', views.recenseamento, name='gerar_documento'),
    path('recensear/', views.RecenseamentoView.as_view(), name='recensear'),
]