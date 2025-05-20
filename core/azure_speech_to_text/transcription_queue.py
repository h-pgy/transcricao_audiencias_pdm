import queue
import time
from typing import List, Optional, Union
from .batch_transcription import AzureBatchTranscriptionJob  # seu módulo
from config import (AZURE_STORAGE_TRANSCRIPTIONS_CONTAINER_NAME,
                    AZURE_SPEECH_KEY,
                    AZURE_SPEECH_REGION
                    )

class TranscriptionQueue:


    def __init__(self, destination_container_url: str,
                azure_speech_subscription_key:Optional[str]=None,
                azure_speech_region:Optional[str]=None, 
                wait_seconds: int = 10,
                max_wait_seconds: int = 10800) -> None:
        

        self.azure_speech_subscription_key = azure_speech_subscription_key or AZURE_SPEECH_KEY
        self.azure_speech_region = azure_speech_region or AZURE_SPEECH_REGION
        self.destination_container_url = destination_container_url

        self.wait_seconds: int = wait_seconds
        self.max_wait_seconds: int = max_wait_seconds
        #iniciar filas
        self.queue_urls = queue.Queue()
        self.queue_jobs = queue.Queue()
        self.finalizadas: List[dict] = []  

        print('fui reimportado')      

    def iniciar_transcricoes(self, urls: Union[str, List[str]]) -> None:

        if isinstance(urls, str):
            urls = [urls]
        print("🚀 Iniciando jobs de transcrição...")
        self.queue_urls.put(urls)
        while not self.queue_urls.empty():
            url = self.queue_urls.get()
            if not isinstance(url, list):
                url = [url]
            job = AzureBatchTranscriptionJob(self.azure_speech_subscription_key, self.azure_speech_region)
            job.initiate_transcription_job(
                audio_sas_urls=url,
                dest_container_url=self.destination_container_url
            )
            self.queue_jobs.put(job)
            print(f"🔁 Job iniciado para {url}")

    def monitorar(self) -> None:

        print("🔍 Monitorando transcrições em andamento...")
        time_passed = 0
        init_time = time.time()
        while not self.queue_jobs.empty():
            job = self.queue_jobs.get()
            status = job.status
            print(f"🧭 Status: {status}")
            if job.is_finished():
                resultado = {
                    'status': status,
                    'url_status': job.status_url,
                    'metadados': job.get_results_metadata()
                }
                self.finalizadas.append(resultado)
                print(f"✅ Finalizado: {status} | {job.status_url}")
            else:
                print("⏳ Ainda em processamento, reenfileirando...")
                self.queue_jobs.put(job)
                passed_time_last_check = time.time() - init_time
                time_passed += passed_time_last_check
                if time_passed > self.max_wait_seconds:
                    print("⏰ Tempo máximo de espera atingido, encerrando monitoramento.")
                    raise TimeoutError("Tempo máximo de espera atingido.")
                time.sleep(self.wait_seconds)
