import requests
from typing import List, Optional
import time
from config import (
    AZURE_SPEECH_REGION,
    AZURE_SPEECH_KEY,
    )

class AzureBatchTranscriptionJob:

    version:str = '3.2'
    default_display_name: str = 'batch_transcription'
    default_language: str = 'pt-BR'

    def __init__(self, subscription_key: str=AZURE_SPEECH_KEY, region: str=AZURE_SPEECH_REGION, language:Optional[str]=None) -> None:
        self.subscription_key = subscription_key
        self.region: str = region
        self.language: str = language or self.default_language
        self.domain: str = f'{self.region}.api.cognitive.microsoft.com'
        self.base_url: str = self.__get_base_url()

    def __get_base_url(self)->str:

        return f'https://{self.domain}/speechtotext/v{self.version}/transcriptions'
    
    @property
    def headers(self)->dict:
        return {
            'Ocp-Apim-Subscription-Key': self.subscription_key,
            'Content-Type': 'application/json'
        }
    
    def initiate_transcription_job(self, audio_sas_urls: List[str], dest_container_url:str, display_name:Optional[str]=None)->None:
        
        if display_name is None:
            display_name = self.default_display_name

        body = {
            'contentUrls' : audio_sas_urls,
            'locale' : self.language,
            'displayName' : display_name,
            'properties' : {
                'wordLevelTimestampsEnabled' : False,
                'punctuationMode' : 'DictatedAndAutomatic',
                'profanityFilterMode' : 'None',
                'destinationContainerUrl' : dest_container_url,
                },
        }
        print(f'Posting to Azure API: {self.base_url}')
        print(body)
        response: requests.Response = requests.post(self.base_url, headers=self.headers, json=body)
        if response.status_code == 201:
            print('Job initiated successfully.')
            self.status_url: str = response.headers["Location"]
        else:
            raise Exception(f"Error initiating transcription job: {response.status_code} - {response.text}")

    @property
    def status(self) -> str:
        
        if not self.status_url:
            raise RuntimeError("Transcrição ainda não foi iniciada.")
        response = requests.get(self.status_url, headers=self.headers)
        if response.status_code == 200:
            self._status = response.json()['status']
            return self._status
        else:
            raise Exception(f"Erro ao consultar status: {response.status_code} - {response.text}")
        
    def get_results_metadata(self) -> Optional[dict]:
        if self.status != "Succeeded":
            return None
        response = requests.get(f"{self.status_url}", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def is_finished(self) -> bool:
        return self.status in ["Succeeded", "Failed"]
    
    
        