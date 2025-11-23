from django.urls import path
from . import views
from django.conf.urls import handler403

# urlpatterns = [
#     path('solicitar_documento/', views.solicitacao_documento, name='solicitar_documento'),
#     path('gerar_documento/', views.gerar_documento, name='gerar_documento'),
#     path('gerar/<str:documento_nome>/', views.gerar_pdf_documento, name='gerar_pdf'),
# ]
handler403 = 'meu_projecto.views.erro_403'
urlpatterns = [
    path('solicitar/', views.solicitar_documento, name='solicitar_documento'),
    path('visualizar/<int:documento_id>/', views.visualizar_documento, name='visualizar_documento'),
    path('gerar_documento/<int:documento_id>/', views.gerar_documento, name='gerar_documento'),
    path('baixar_pdf/<int:documento_id>/', views.gerar_pdf_documento, name='baixar_pdf_documento'),
]