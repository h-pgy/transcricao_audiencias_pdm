from urllib.parse import urlparse
from itertools import zip_longest
import pandas as pd
import Levenshtein

class ResultParser:

    def extract_file_name(self, json_data:dict)->str:
    
        url = json_data['source']
        endpoint = urlparse(url).path.split('/')[-1]
        return endpoint
    
    def get_audiencia_from_file(self, file_name:str)->str:

        return file_name.replace('_clip.wav', '')
    
    def get_transcription_duration_minutes(self, json_data:dict)->float:
    
        return json_data['durationMilliseconds'] / 60000
    
    def extract_frases_by_channel(self, json_data:dict, channel_id:int)->list:

        return [f for f in json_data['recognizedPhrases'] if f['channel'] == channel_id]
    
    def zip_channels(self, channel_1:list, channel_2:list)->list:

        return list(zip_longest(channel_1, channel_2, fillvalue=None))
    
    def get_best_guess_frase_list(self, frase_list:list[dict])->dict:

        return max(frase_list, key=lambda x: x.get('confidence', 0))
    
    def get_best_guess_frase_channel(self, channel_prediction:dict)->dict:

        n_best_frases = channel_prediction['nBest']

        return self.get_best_guess_frase_list(n_best_frases)
    

    def calc_frase_similarity(self, frase_1:str, frase_2:str)->float:

        return Levenshtein.ratio(frase_1, frase_2)
    
    def check_guess_similarity(self, guess_1:dict, guess_2:dict)->float:

        frase_1 = guess_1['lexical']
        frase_2 = guess_2['lexical']

        similarity = self.calc_frase_similarity(frase_1, frase_2)

        if similarity < 0.8:
            raise RuntimeError(f'Frase mismatch: {frase_1} X {frase_2}')
        
        return similarity

    def get_best_guess_frase_channel_pair(self, channel_pair:list[dict])->dict:

        if channel_pair[0] is None:
            return self.get_best_guess_frase_channel(channel_pair[1])
        elif channel_pair[1] is None:
            return self.get_best_guess_frase_channel(channel_pair[0])
        else:
            best_0 = self.get_best_guess_frase_channel(channel_pair[0])
            best_1 = self.get_best_guess_frase_channel(channel_pair[1])
            #checa se as frases estão batendo
            self.check_guess_similarity(best_0, best_1)

            return self.get_best_guess_frase_list([best_0, best_1])
        
    def get_frases_pipeline(self, json_data:dict)->list:

        channel_1 = self.extract_frases_by_channel(json_data, 0)
        channel_2 = self.extract_frases_by_channel(json_data, 1)

        channel_pair = self.zip_channels(channel_1, channel_2)

        best_guess_frase_list = [self.get_best_guess_frase_channel_pair(pair) for pair in channel_pair]

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
                'duration_audiencia':duration,
                'frase':frase['display'],
                'confidence':frase['confidence'],

            }

            final_data.append(data)
        
        return pd.DataFrame(final_data)
    
    def __call__(self, json_data:dict)->pd.DataFrame:

        return self.pipeline(json_data)

            

    
