from urllib.parse import urlparse
from itertools import zip_longest
import pandas as pd
import Levenshtein
from collections import deque
from typing import Deque

class ResultParser:

    min_frase_similarity = 0.8

    def extract_file_name(self, json_data:dict)->str:
    
        url = json_data['source']
        endpoint = urlparse(url).path.split('/')[-1]
        return endpoint
    
    def get_audiencia_from_file(self, file_name:str)->str:

        return file_name.replace('_clip.wav', '')
    
    def get_transcription_duration_minutes(self, json_data:dict)->float:
    
        return json_data['durationMilliseconds'] / 60000
    
    def extract_predictions_by_channel(self, json_data:dict, channel_id:int)->list[dict]:

        predictions: list[dict] = [f for f in json_data['recognizedPhrases'] if f['channel'] == channel_id
                and f['recognitionStatus']=='Success']
        
        return predictions
    
    def zip_channels_queue(self, channel_1:list, channel_2:list)->Deque:

        list_channels =  list(zip_longest(channel_1, channel_2, fillvalue=None))
        fila = deque()
        for item in list_channels:
            fila.append(list(item))
        return fila
    
    def get_best_guess_frase(self, nbest_frases:list[dict])->dict:

        return max(nbest_frases, key=lambda x: x.get('confidence', 0))
    
    def get_best_guess_frase_channel(self, channel_prediction:dict)->dict:

        n_best_frases = channel_prediction['nBest']
        frase = self.get_best_guess_frase(n_best_frases)

        frase['channel'] = channel_prediction['channel']
        frase['offset'] = channel_prediction['offsetMilliseconds']
        frase['duration'] = channel_prediction['durationMilliseconds']

        return frase

    def calc_frase_similarity(self, frase_1:str, frase_2:str)->float:

        return Levenshtein.ratio(frase_1, frase_2)
    
    def get_frase_similarity(self, guess_1:dict, guess_2:dict)->float:

        frase_1 = guess_1['lexical']
        frase_2 = guess_2['lexical']

        similarity = self.calc_frase_similarity(frase_1, frase_2)

        return similarity
    
    def get_best_guess_frase_pair_full(self, channel_pair:list[dict], channel_pair_queu:Deque)->dict:

        best_0 = self.get_best_guess_frase_channel(channel_pair[0])
        best_1 = self.get_best_guess_frase_channel(channel_pair[1])
        
        #checa se as frases estão batendo
        similarity = self.get_frase_similarity(best_0, best_1)

        if similarity <= self.min_frase_similarity:
            
            #se as frases não baterem, pega a primeira frase cronologicamente
            #e devolve a outra frase para a fila
            min_offset: dict = min([best_0, best_1], key=lambda x: x['offset'])
            min_offset_channel = int(min_offset['channel'])
            channel_pair[min_offset_channel] = None
            channel_pair_queu.appendleft(channel_pair)

            return min_offset

        return self.get_best_guess_frase([best_0, best_1])

    def get_best_guess_frase_channel_pair(self, channel_pair_queu:Deque)->dict:

        channel_pair = channel_pair_queu.popleft()

        if channel_pair[0] is None:
            return self.get_best_guess_frase_channel(channel_pair[1])
        elif channel_pair[1] is None:
            return self.get_best_guess_frase_channel(channel_pair[0])
        else:
            return self.get_best_guess_frase_pair_full(channel_pair, channel_pair_queu)
        
    def get_frases_pipeline(self, json_data:dict)->list:

        channel_1 = self.extract_predictions_by_channel(json_data, 0)
        channel_2 = self.extract_predictions_by_channel(json_data, 1)

        channel_pair_queue = self.zip_channels_queue(channel_1, channel_2)

        best_guess_frase_list = []
        while channel_pair_queue:
            best_frase = self.get_best_guess_frase_channel_pair(channel_pair_queue)
            best_guess_frase_list.append(best_frase)

        return best_guess_frase_list
    
    def pipeline(self, json_data:dict)->pd.DataFrame:

        #extrai o nome do arquivo
        file_name = self.extract_file_name(json_data)
        #extrai a audiencia
        audiencia = self.get_audiencia_from_file(file_name)
        #extrai a duração
        duration = self.get_transcription_duration_minutes(json_data)
        #extrai as frases
        frases = self.get_frases_pipeline(json_data)

        final_data = []
        for i, frase in enumerate(frases):
            data = {
                'audiencia':audiencia,
                'file_name':file_name,
                'duration_audiencia':duration,
                'frase':frase['display'],
                'confidence':frase['confidence'],
                'channel':frase['channel'],
                'offset':frase['offset'],
                'duration':frase['duration'],
            }

            final_data.append(data)
        
        return pd.DataFrame(final_data)
    
    def __call__(self, json_data:dict)->pd.DataFrame:

        return self.pipeline(json_data)

            

    
