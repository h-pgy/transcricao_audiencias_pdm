import yt_dlp
import os
from typing import Optional
from utils.path import solve_path
from utils.url import is_url, get_domain
from config import WAV_FOLDER

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

    def __yt_dlp_save_options(self, dest_file_path:str)->str:
        
        options = {
            'format': 'bestaudio/best',
            'outtmpl': dest_file_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'quiet': False
        }

        return options
    
    def download_youtube_audio(self, url:str, dest_file_name:str)->str:

        url = self.__check_url(url)
        print('Downloading audio from URL:', url)
        dest_file_path = self.__file_path(dest_file_name)
        print('Destination file name:', dest_file_path)
        options = self.__yt_dlp_save_options(dest_file_path)

        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
        
        #fix para quando ele adiciona o .wav no final do nome do arquivo
        if os.path.exists(dest_file_path + '.wav'):
            os.rename(dest_file_path + '.wav', dest_file_path)

        return dest_file_path

    def __call__(self, url:str, dest_file_name:str)->str:
        return self.download_youtube_audio(url, dest_file_name)