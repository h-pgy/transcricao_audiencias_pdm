import requests
from typing import List, Optional
import time
from config import AZURE_SPEECH_KEY, AZURE_SPEECH_REGION

class AzureBatchTranscriptionClient:

    version:str = '3.2'

    def __init__(self, subscription_key: str, region: str, language: str = 'pt-BR') -> None:
        self.subscription_key = subscription_key
        self.region: str = region
        self.language: str = language
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
    
    def initiate_transcription_job(self, audio_sas_urls: List[str], display_name: str = 'batch_transcription') -> str:
        
        body = {
            'diarizationEnabled' : True,
            'contentUrls' : audio_sas_urls,
            'locale' : self.language,
            'displayName' : display_name
        }
        print(f'Posting to Azure API: {self.base_url}')
        response: requests.Response = requests.post(self.base_url, headers=self.headers, json=body)
        if response.status_code == 201:
            return response.headers["Location"]
        else:
            raise Exception(f"Error initiating transcription job: {response.status_code} - {response.text}")

    def check_transcription_job_status(self, status_url: str) -> dict:    

        response: requests.Response = requests.get(status_url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error checking transcription job status: {response.status_code} - {response.text}")
        
    
    def __call__(self, audio_sas_urls: List[str], display_name: str = 'batch_transcription') -> Optional[dict]:
        """
        Initiate a batch transcription job and check its status.
        """
        # Start the transcription job
        status_url = self.initiate_transcription_job(audio_sas_urls, display_name)
        print(f"Transcription job started. Status URL: {status_url}")
        # Check the status of the transcription job
        while True:
            status_response = self.check_transcription_job_status(status_url)
            print(f"Transcription job status: {status_response['status']}")
            if status_response['status'] in ['Succeeded', 'Failed']:
                break
            # Wait for a while before checking the status again
            time.sleep(10)
            print('Waiting for 10 seconds before checking the status again...')
        # Return the transcription result
        if status_response['status'] == 'Succeeded':
            print(status_response)
            with requests.get(status_response['links']['files'], headers=self.headers) as r:
                resp = r.json()
                print('*'*40)
                print(resp)
                print('*'*40)
                new_url = resp['values'][0]['links']['contentUrl']
                with requests.get(new_url, headers=self.headers) as r:
                    print(r.json())
        else:
            print(f"Transcription job failed: {status_response['message']}")
            return None
        