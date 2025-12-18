import re
import pytesseract
from PIL import Image


def extrair_numero_bi(caminho_imagem):
    """
    Extrai número de BI moçambicano via OCR.
    Exemplo: 110102345678A
    """
    try:
        texto = pytesseract.image_to_string(
            Image.open(caminho_imagem),
            lang="por"
        )

        texto = texto.upper().replace(" ", "")

        padrao = r"\b\d{12}[A-Z]\b"
        match = re.search(padrao, texto)

        if match:
            return match.group()

    except Exception:
        pass

    return None
