import tempfile
import os
from django.core.exceptions import ValidationError
from django.conf import settings

def salvar_temp_upload(uploaded_file):
    temp = tempfile.NamedTemporaryFile(delete=False)
    for chunk in uploaded_file.chunks():
        temp.write(chunk)
    temp.flush()
    return temp.name


def get_file_path(file_obj, prefix):
    """
    Retorna o caminho físico de um arquivo.
    Pode ser um UploadedFile (novo) ou FileField já existente.
    """
    import tempfile, os

    # Se for UploadedFile
    if hasattr(file_obj, "read"):
        with tempfile.NamedTemporaryFile(delete=False, prefix=prefix) as tmp:
            tmp.write(file_obj.read())
            return tmp.name

    # Se for FileField já existente
    if hasattr(file_obj, "path") and os.path.exists(file_obj.path):
        return file_obj.path

    # Se for string com caminho
    if isinstance(file_obj, str) and os.path.exists(file_obj):
        return file_obj

    raise ValidationError(f"{prefix} inválido ou arquivo não encontrado.")

