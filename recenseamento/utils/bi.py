import re

def extrair_numero_bi(texto):
    if not texto:
        return None

    texto = texto.upper()

    # Remove espaços excessivos
    texto = re.sub(r"\s+", " ", texto)

    # PADRÕES COMUNS DO BI DE MOÇAMBIQUE
    padroes = [
        r"\b\d{13}\b",                         # 13 dígitos seguidos
        r"\b\d{6}\s?\d{6}\s?[A-Z]\b",          # 110100 123456 A
        r"\b\d{6}/\d{6}/[A-Z]\b",              # 110100/123456/A
        r"\b\d{6}-\d{6}-[A-Z]\b",              # 110100-123456-A
    ]

    for padrao in padroes:
        match = re.search(padrao, texto)
        if match:
            numero = match.group()

            # Normalizar → só letras e números
            numero = re.sub(r"[^A-Z0-9]", "", numero)
            return numero

    return None
