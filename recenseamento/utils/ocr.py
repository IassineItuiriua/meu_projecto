# recenseamento/utils/ocr.py
import re

def normalizar_texto_ocr(texto):
    texto = texto.upper()
    texto = texto.replace("O", "0").replace("I", "1").replace("L", "1")
    texto = re.sub(r"[^A-Z0-9]", "", texto)
    return texto

def extrair_numero_bi(texto):
    texto = normalizar_texto_ocr(texto)

    # padrão mais comum em BI moçambicano
    match = re.search(r"\d{11,13}[A-Z]", texto)
    if match:
        return match.group()

    # fallback apenas números
    match = re.search(r"\d{11,13}", texto)
    if match:
        return match.group()

    return None
