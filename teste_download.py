import yt_dlp

def baixar_audio_para_wav(url, destino='audio.wav'):
    opcoes = {
        'format': 'bestaudio/best',
        'outtmpl': destino,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'quiet': False
    }

    with yt_dlp.YoutubeDL(opcoes) as ydl:
        ydl.download([url])

# Exemplo de uso:
video_url = 'https://www.youtube.com/shorts/YSq1P7XfWmg'  # Substitua por qualquer URL real
baixar_audio_para_wav(video_url)
