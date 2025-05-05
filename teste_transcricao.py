import os
import wave
import json
from datetime import datetime
import threading
import azure.cognitiveservices.speech as speechsdk

from config import AZURE_SPEECH_KEY, AZURE_SPEECH_REGION

LIMITE_SEGUNDOS = 5 * 60 * 60  # 5 horas = 18.000 segundos
LOG_PATH = "log_transcricoes.json"
USO_ESTIMADO_ATUAL_SEGUNDOS = 0

# Carrega uso acumulado e histórico
if os.path.exists(LOG_PATH):
    with open(LOG_PATH, 'r', encoding='utf-8') as f:
        log_data = json.load(f)
        USO_ESTIMADO_ATUAL_SEGUNDOS = sum(item['duracao_segundos'] for item in log_data)
else:
    log_data = []

def duracao_audio_wav(caminho_audio):
    with wave.open(caminho_audio, 'rb') as wav_file:
        frames = wav_file.getnframes()
        taxa = wav_file.getframerate()
        return frames / float(taxa)

def transcrever_e_salvar(arquivo_wav, chave, regiao, pasta_saida='transcricoes'):
    global USO_ESTIMADO_ATUAL_SEGUNDOS, log_data

    duracao = duracao_audio_wav(arquivo_wav)
    print(f'Duração do arquivo: {duracao}')
    if USO_ESTIMADO_ATUAL_SEGUNDOS + duracao > LIMITE_SEGUNDOS:
        raise Exception("⚠️ Limite estabelecido foi atingido. Transcrição interrompida.")

    speech_config = speechsdk.SpeechConfig(subscription=chave, region=regiao)
    speech_config.speech_recognition_language = "pt-BR"

    audio_input = speechsdk.AudioConfig(filename=arquivo_wav)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    resultado_final = []

def transcrever_e_salvar(arquivo_wav, chave, regiao, pasta_saida='transcricoes'):
    global USO_ESTIMADO_ATUAL_SEGUNDOS, log_data

    duracao = duracao_audio_wav(arquivo_wav)
    print(f'Duração do arquivo: {duracao}')
    if USO_ESTIMADO_ATUAL_SEGUNDOS + duracao > LIMITE_SEGUNDOS:
        raise Exception("⚠️ Limite estabelecido foi atingido. Transcrição interrompida.")

    speech_config = speechsdk.SpeechConfig(subscription=chave, region=regiao)
    speech_config.speech_recognition_language = "pt-BR"

    audio_input = speechsdk.AudioConfig(filename=arquivo_wav)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    resultado_final = []

    done = threading.Event()

    def handle_result(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            resultado_final.append(evt.result.text)

    def handle_stop(evt):
        print("Sessão encerrada.")
        done.set()

    def handle_cancel(evt):
        print(f"Transcrição cancelada: {evt.reason}")
        done.set()

    recognizer.recognized.connect(handle_result)
    recognizer.session_stopped.connect(handle_stop)
    recognizer.canceled.connect(handle_cancel)

    recognizer.start_continuous_recognition()
    print("Transcrevendo...")

    # Aguarda até o fim ou timeout baseado na duração do áudio
    done.wait(timeout=int(duracao) + 10)
    recognizer.stop_continuous_recognition()

    texto = " ".join(resultado_final) if resultado_final else "[ERRO] Nenhuma fala reconhecida."

    USO_ESTIMADO_ATUAL_SEGUNDOS += duracao

    os.makedirs(pasta_saida, exist_ok=True)
    base_nome = os.path.splitext(os.path.basename(arquivo_wav))[0]
    caminho_txt = os.path.join(pasta_saida, f"{base_nome}.txt")

    with open(caminho_txt, 'w', encoding='utf-8') as f:
        f.write(texto)

    entrada_log = {
        "arquivo_audio": arquivo_wav,
        "arquivo_txt": caminho_txt,
        "duracao_segundos": round(duracao, 2),
        "timestamp": datetime.now().isoformat(),
        "resumo_transcricao": texto[:200],
        "uso_total_estimado": round(USO_ESTIMADO_ATUAL_SEGUNDOS, 2)
    }
    log_data.append(entrada_log)

    with open(LOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)

    return texto


if __name__ == "__main__":

    print(USO_ESTIMADO_ATUAL_SEGUNDOS)
    t = transcrever_e_salvar('audio.wav.wav', AZURE_SPEECH_KEY, AZURE_SPEECH_REGION)
    print(t)
    print(USO_ESTIMADO_ATUAL_SEGUNDOS)
