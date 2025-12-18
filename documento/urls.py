# documento/urls.py
from django.urls import path
from . import views

app_name = "documento"

urlpatterns = [
    path('solicitar/', views.SolicitarDocumentoView.as_view(), name='solicitar_documento'),
    path('visualizar/<int:documento_id>/', views.VisualizarDocumentoView.as_view(), name='visualizar_documento'),
    path('gerar_documento/<int:documento_id>/', views.GerarDocumentoView.as_view(), name='gerar_documento'),
    path('baixar_pdf/<int:documento_id>/', views.BaixarPDFDocumentoView.as_view(), name='baixar_pdf_documento'),
    path('documento/confirmar_exame/<int:pessoa_id>/', views.ConfirmarExameView.as_view(), name="confirmar_exame"),
]





# from django.urls import path
# from . import views
# from django.conf.urls import handler403

# app_name = "documento"
# handler403 = 'meu_projecto.views.erro_403'
# urlpatterns = [
#     path('solicitar/', views.solicitar_documento, name='solicitar_documento'),
#     path('visualizar/<int:documento_id>/', views.visualizar_documento, name='visualizar_documento'),
#     path('gerar_documento/<int:documento_id>/', views.gerar_documento, name='gerar_documento'),
#     path('baixar_pdf/<int:documento_id>/', views.gerar_pdf_documento, name='baixar_pdf_documento'),
#     path('documento/confirmar_exame/<int:pessoa_id>/', views.confirmar_exame, name="confirmar_exame"),

# ]