import pytest
import os
from core.youtube_download.download_audio import YoutubeAudioDownloader
import shutil

@pytest.fixture
def downloader(tmp_path='teste_path'):

    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)
    try:
        yield YoutubeAudioDownloader(tmp_path)
    finally:
        shutil.rmtree(tmp_path)


def test_download_youtube_audio_rejeita_url_invalida(downloader):
    with pytest.raises(ValueError, match="Must be valid url"):
        downloader.download_youtube_audio("not_a_url", "audio.wav")

def test_download_youtube_audio_rejeita_url_nao_youtube(downloader):
    with pytest.raises(ValueError, match="Must be youtube url"):
        downloader.download_youtube_audio("https://vimeo.com/12345", "audio.wav")

def test_download_youtube_audio_rejeita_nome_sem_extensao_wav(downloader):
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    with pytest.raises(ValueError, match="Must be .wav file"):
        downloader.download_youtube_audio(url, "audio.mp3")