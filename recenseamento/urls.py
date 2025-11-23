from django.urls import path
from . import views

urlpatterns = [
    #path('painel/', views.recenseamento, name='painel'),
    # path('gerar_documento/', views.recenseamento, name='gerar_documento'),
    path('recensear/', views.recenseamento, name='recensear'),
]