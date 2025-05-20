from azure.storage.blob import BlobServiceClient
from typing import List, Optional, Union
import os
import json
import re
from utils.path import create_folder_if_not_exists, solve_path
from config import (DATA_FOLDER, 
                    AZURE_STORAGE_CONNECTION_STRING, 
                    )


class BlobStorageDataFetcher:

    def __init__(self, container_name:str,
                connection_string: str=AZURE_STORAGE_CONNECTION_STRING,
                data_folder:str=DATA_FOLDER,
                ):
        """
        Initializes the BlobStorageDataFetcher with the connection string and container name.
        
        Args:
            connection_string (str): The connection string for the Azure Blob Storage account.
            container_name (str): The name of the container in the Blob Storage account.
        """

        self.container_name = container_name
        self.connection_string = connection_string
        self.data_folder = create_folder_if_not_exists(data_folder)
        self.__init_client()

    def __init_client(self) -> None:
        """
        Initializes the BlobServiceClient and ContainerClient.
        """
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.container_name)

    @property
    def blob_list(self) -> List[str]:
        """
        Returns a list of blob names in the container.
        
        Returns:
            List[str]: A list of blob names in the container.
        """
        return [blob.name for blob in self.container_client.list_blobs()]
    
    def find_blob(self, search_term: str) -> Optional[list[str]]:
        """
        Finds a blob in the container by its name.
        
        Args:
            search_term (str): The search term of the blob to find based on blob name.
        
        Returns:
            Optional[str]: The name of the blob if found, None otherwise.
        """
        found = []
        for blob_name in self.blob_list:
            if re.search(search_term, blob_name):
                found.append(blob_name)
        if found:
            return found
        return None
    
    def download_blob_to_memory(self, blob_name: str, decode:bool=False, encoding='utf-8') -> Union[str, bytes]:
        """
        Downloads a blob from the container to memory.
        
        Args:
            blob_name (str): The name of the blob to download.
        """

        if blob_name not in self.blob_list:
            raise ValueError(f"Blob {blob_name} not found in container {self.container_name}.")
        
        data = self.container_client.download_blob(blob_name).readall()
        if decode:
            data = data.decode(encoding)
        return data

    def __solve_file_path(self, file_path: str) -> str:

        return solve_path(file_path, self.data_folder)
    
    def download_blob_to_file(self, blob_name: str, file_name: str, as_text:bool=False) -> None:
        """
        Downloads a blob from the container to a file.
        
        Args:
            blob_name (str): The name of the blob to download.
            file_path (str): The path to save the downloaded blob.
        """
        if blob_name not in self.blob_list:
            raise ValueError(f"Blob {blob_name} not found in container {self.container_name}.")
        
        write_mode = 'wb' if not as_text else 'w'
        file_path = self.__solve_file_path(file_name)
        with open(file_path, write_mode) as file:
            file.write(self.download_blob_to_memory(blob_name, decode=as_text))
        return os.path.abspath(file_path)
    
    def download_blob_to_json(self, blob_name: str) -> dict:
        """
        Downloads a blob from the container and parses it as JSON.
        
        Args:
            blob_name (str): The name of the blob to download.
        
        Returns:
            dict: The parsed JSON data.
        """
        blob_data = self.download_blob_to_memory(blob_name, decode=True)
        return json.loads(blob_data)
    
    def download_blob(self, blob_name:str, 
                      file_name:Optional[str]=None, 
                      as_text:bool=False, 
                      as_json:bool=False) -> Union[str, dict]:
        """
        Downloads a blob from the container to a file or returns its content.
        
        Args:
            blob_name (str): The name of the blob to download.
            file_path (str): The path to save the downloaded blob. If None, the blob will be returned as a string or dict.
            as_text (bool): If True, the blob will be returned as a string. Default is False.
            as_json (bool): If True, the blob will be parsed as JSON. Default is False.
        
        Returns:
            Union[str, dict]: The content of the blob as a string or dict.
        """

        if file_name is None:
            if as_json:
                return self.download_blob_to_json(blob_name)
            return self.download_blob_to_memory(blob_name, decode=as_text)
        
        else:
            if as_json or as_text:
                file_path = self.download_blob_to_file(blob_name, file_name, as_text=True)
            else:
                file_path = self.download_blob_to_file(blob_name, file_name, as_text=as_text)
            
            return file_path
        

    def __call__(self, blob_name:str, 
                 file_name:Optional[str]=None, 
                 as_text:bool=False, 
                 as_json:bool=False) -> Union[str, dict]:
        """
        Calls the download_blob method to download a blob.
        
        Args:
            blob_name (str): The name of the blob to download.
            file_path (str): The path to save the downloaded blob. If None, the blob will be returned as a string or dict.
            as_text (bool): If True, the blob will be returned as a string. Default is False.
            as_json (bool): If True, the blob will be parsed as JSON. Default is False.
        
        Returns:
            Union[str, dict]: The content of the blob as a string or dict.
        """
        return self.download_blob(blob_name, file_name=file_name, as_text=as_text, as_json=as_json)
    
    
