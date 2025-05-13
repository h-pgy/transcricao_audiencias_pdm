from core.youtube_download.download_audio import YoutubeAudioDownloader
import os

if __name__=='__main__':
    # Test the YoutubeAudioDownloader class
    downloader = YoutubeAudioDownloader()
    url = 'https://www.youtube.com/shorts/0v7KlAS0kH0'  # Replace with a valid YouTube URL
    output_path = 'test_audio1.wav'  # Replace with your desired output path

    # Download the audio
    file = downloader(url, output_path)
    print(f"Audio downloaded to: {file}")
    # Check if the file exists
    assert os.path.isfile(file)
    delete = input('Delete file? (y/n): ')
    if delete.lower() == 'y':
        os.remove(file)
        print(f"File {file} deleted.")
    else:
        print(f"File {file} not deleted.")

