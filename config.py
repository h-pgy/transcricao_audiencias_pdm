import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env
load_dotenv()

AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
    raise EnvironmentError("Chave ou região da Azure não configuradas no .env")
