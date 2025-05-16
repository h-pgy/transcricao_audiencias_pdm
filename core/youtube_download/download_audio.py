import yt_dlp
import os
import subprocess
from typing import Optional, Union
from utils.path import solve_path
from utils.time import validar_timestamp_video
from utils.url import is_url, get_domain
from config import WAV_FOLDER, COOKIES_FILE_NAME

class YoutubeAudioDownloader:

    def __init__(self, save_folder:Optional[str]=None)->None:

        if save_folder is None:
            self.save_folder = WAV_FOLDER
        else:
            if not os.path.exists(save_folder):
                raise ValueError(f'Save folder does not exist.')
            self.save_folder = save_folder

    
    def __file_path(self, file_name:str)->str:
        
        if not file_name.endswith('.wav'):
            raise ValueError(f"Must be .wav file: {file_name}")
        
        return solve_path(file_name, self.save_folder)
    
    def __check_url(self, url:str)->str:

        if not is_url(url):
            raise ValueError(f'Must be valid url: {url}')
        
        if 'youtube' not in get_domain(url):
            raise ValueError('Must be youtube url.')
        
        return url
    
    def __yt_dlp_save_options(self, dest_file_path:str)->dict:
        

        options: dict = {
            'format': 'bestaudio/best',
            'outtmpl': dest_file_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'quiet': False,
        }

        if os.path.exists(COOKIES_FILE_NAME):
            options['cookiefile'] = COOKIES_FILE_NAME

        return options
    

    def __validate_interval(self, begining:Optional[str], end:Optional[str])->Union[None, str]:

        if begining is not None:
            if not validar_timestamp_video(begining):
                raise ValueError(f"Invalid begining timestamp: {begining}")
            
        if end is not None:
            if not validar_timestamp_video(end):
                raise ValueError(f"Invalid begining timestamp: {begining}")
    

    def __clip_audio(self, file_path:str, begining:str, end:Optional[str])->str:

        if not os.path.exists(file_path) or not file_path.endswith('.wav'):
            raise ValueError(f"File does not exist or is not a .wav file: {file_path}")

        self.__validate_interval(begining, end)

        # gerando nome do arquivo de saída
        dest_file: str = file_path.replace('.wav', '_clip.wav')

        #inicio do comando
        comando = [
            "ffmpeg",
            "-y",  # sobrescreve sem perguntar
            "-i", file_path,
            "-ss", begining,  # tempo de início
        ]

        # se o tempo de fim for fornecido, adiciona ao comando
        if end is not None:
            comando += ["-to", end]
        
        # final do comando
        comando += [
            "-c", "copy",  # sem reencodar
            dest_file  # nome do arquivo de saída
        ]

        resultado: subprocess.CompletedProcess[bytes] = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if resultado.returncode != 0:
            raise RuntimeError(f"Erro ao cortar áudio com ffmpeg:\n{resultado.stderr.decode()}")
        else:
            print(f"🎧 Áudio cortado salvo em: {file_path}")
            return dest_file

    
    def download_youtube_audio(self, url:str, dest_file_name:str, begining:Optional[str]=None, end:Optional[str]=None)->str:

        url = self.__check_url(url)
        print('Downloading audio from URL:', url)
        dest_file_path: str = self.__file_path(dest_file_name)
        print('Destination file name:', dest_file_path)
        options: dict = self.__yt_dlp_save_options(dest_file_path)
        print('Options:', options)
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
        
        #fix para quando ele adiciona o .wav no final do nome do arquivo
        if os.path.exists(dest_file_path + '.wav'):
            os.rename(dest_file_path + '.wav', dest_file_path)

        if begining is not None:
            self.__clip_audio(dest_file_path, begining, end)

        return dest_file_path

    def __call__(self, url:str, dest_file_name:str, begining:Optional[str]=None, end:Optional[str]=None)->str:
        return self.download_youtube_audio(url, dest_file_name, begining, end)