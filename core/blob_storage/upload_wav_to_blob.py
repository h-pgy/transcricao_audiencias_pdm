from typing import Optional
from utils.path import solve_path, create_folder_if_not_exists
from .blob_utils import BlobStorageUploader, BlobStorageSasTokenGenerator

from config import (
            AZURE_STORAGE_CONNECTION_STRING,
            AZURE_STORAGE_CONTAINER_NAME,
            WAV_FOLDER, 
                      )

class WavToBlobUploader:
    """
    Class to upload WAV files to Azure Blob Storage.
    """
    def __init__(self, connection_string: str = AZURE_STORAGE_CONNECTION_STRING, 
                 container_name: str = AZURE_STORAGE_CONTAINER_NAME, file_folder:str=WAV_FOLDER) -> None:
        
        self.blob_uploader = BlobStorageUploader(connection_string)
        self.container_name: str = container_name
        
        self.file_folder: str = create_folder_if_not_exists(file_folder)

        self.generate_sas_token = BlobStorageSasTokenGenerator(connection_string)

    def __get_file_path(self, file_path: str) -> str:

        return solve_path(file_path, self.file_folder)

    def upload_wav(self, file_name: str, blob_name:Optional[str]=None) -> str:
        """
        Upload a WAV file to Azure Blob Storage.
        """

        file_path = self.__get_file_path(file_name)
        if blob_name is None:
            blob_name = file_name

        self.blob_uploader(self.container_name, blob_name, file_path, content_type = 'audio/wav')
        print(f"Uploaded {file_path} to {self.container_name}/{blob_name}")

        token: str = self.generate_sas_token(self.container_name, blob_name)

        return token
    
    def __call__(self, file_name: str, blob_name:Optional[str]=None) -> str:
        """
        Upload a WAV file to Azure Blob Storage.
        """
        return self.upload_wav(file_name, blob_name)

