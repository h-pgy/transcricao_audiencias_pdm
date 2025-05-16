import re

def validar_timestamp_video(timestamp: str) -> bool:
    """
    Verifica se o timestamp está no formato HH:MM:SS, MM:SS ou SS, com valores válidos.
    """
    padrao = r"^(\d{1,2}(:[0-5]?\d){0,2})$"  # cobre SS, MM:SS, HH:MM:SS

    if not re.match(padrao, timestamp):
        return False

    partes = list(map(int, timestamp.split(":")))

    if len(partes) == 1:  # SS
        ss = partes[0]
        return 0 <= ss < 60
    elif len(partes) == 2:  # MM:SS
        mm, ss = partes
        return 0 <= mm < 60 and 0 <= ss < 60
    elif len(partes) == 3:  # HH:MM:SS
        hh, mm, ss = partes
        return 0 <= mm < 60 and 0 <= ss < 60
    else:
        return False
