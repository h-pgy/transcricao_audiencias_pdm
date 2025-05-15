import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from azure.storage.blob import (
    BlobServiceClient, 
    ContentSettings, 
    generate_blob_sas, 
    generate_container_sas,
    BlobSasPermissions,
    ContainerSasPermissions
)

from config import SAS_TTL_SECONDS


def conect_blob_storage(connection_string: str) -> BlobServiceClient:
    """
    Connect to Azure Blob Storage using the provided connection string.
    """
    return BlobServiceClient.from_connection_string(connection_string)



class BlobStorageUploader:

    def __init__(self, connection_string: str) -> None:
        """
        Initializes the BlobUtils class with a connection string and sets up the BlobServiceClient.

        Args:
            connection_string (str): The connection string used to authenticate and connect to the blob storage service.
        """

        self.conn_string: str = connection_string
        self.blob_service_client: BlobServiceClient = conect_blob_storage(self.conn_string)
        self.account_name: str = self.blob_service_client.account_name

    def __solve_blob_name(self, file_path:str, blob_name:Optional[str]) -> str:

        if blob_name is None:
            blob_name = os.path.basename(file_path)

        return blob_name

    
    def upload_blob(self, container_name: str, file_path: str, blob_name:Optional[str]=None, **content_settings) -> None:
        """
        Upload a file to Azure Blob Storage.
        """
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        if content_settings:
            content_settings = ContentSettings(**content_settings)
        else:
            content_settings = ContentSettings()
        
        blob_name = self.__solve_blob_name(file_path, blob_name)

        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True, content_settings=content_settings)

    def __call__(self, container_name: str, file_path: str,  blob_name:Optional[str]=None, **content_settings) -> None:
        """
        Upload a file to Azure Blob Storage.
        """
        self.upload_blob(container_name, file_path, blob_name, **content_settings)



class BlobStorageSasTokenGenerator:

    def __init__(self, connection_string: str, sas_ttl_seconds: Optional[int] = None) -> None:

        self.conn_string: str = connection_string
        self.sas_ttl_seconds: int = sas_ttl_seconds if sas_ttl_seconds else SAS_TTL_SECONDS
        self.blob_service_client: BlobServiceClient = conect_blob_storage(self.conn_string)
        self.account_name: str = self.blob_service_client.account_name

    def __solve_expiry_time(self, expiry_seconds: Optional[int]) -> datetime:
        """
        Calculate the expiry time for the SAS token.
        """
        if expiry_seconds is None:
            expiry_seconds = self.sas_ttl_seconds
        return datetime.now(timezone.utc) + timedelta(seconds=expiry_seconds)

    def generate_blob_sas_token(self, container_name: str, blob_name: str, expiry_seconds: Optional[int] = None) -> str:
        """
        Generate a SAS token for a blob in Azure Blob Storage with only read permissions.
        """
        
        expiry_time: datetime = self.__solve_expiry_time(expiry_seconds)

        sas_token = generate_blob_sas(
            account_name=self.blob_service_client.account_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=self.blob_service_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=expiry_time
        )

        return sas_token
    
    def generate_container_sas_token(self, container_name: str, expiry_seconds: Optional[int] = None) -> str:
        """
        Generate a SAS token for a container in Azure Blob Storage with only read permissions.
        """
        
        expiry_time: datetime = self.__solve_expiry_time(expiry_seconds)

        sas_token = generate_container_sas(
            account_name=self.blob_service_client.account_name,
            container_name=container_name,
            account_key=self.blob_service_client.credential.account_key,
            permission=ContainerSasPermissions(read=True, write=True, add=True, create=True, list=True, execute=True),
            expiry=expiry_time
        )

        return sas_token
    
    def build_blob_sas_url(self, container_name: str, blob_name: str, sas_token:str) -> str:
        """
        Generate a SAS URL for a blob in Azure Blob Storage based on passed token.
        """
        
        url = f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"

        return url
    
    def builb_container_sas_url(self, container_name: str, sas_token:str) -> str:
        """
        Generate a SAS URL for a container in Azure Blob Storage based on passed token.
        """
        
        url = f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{container_name}?{sas_token}"

        return url
    
    def __call__(self, container_name: str, blob_name: Optional[str]=None, expiry_seconds: Optional[int] = None, 
                 blob_token:bool=False, container_token:bool=True, url:bool=True) -> str:
        """
        Generate a SAS token for a blob in Azure Blob Storage with only read permissions.
        """

        if blob_token:
            if blob_name is None:
                raise ValueError("blob_name must be provided when blob_token is True.")
            token = self.generate_blob_sas_token(container_name, blob_name, expiry_seconds)
            if not url:
                return token
            return self.build_blob_sas_url(container_name, blob_name, token)
        
        elif container_token:
            token = self.generate_container_sas_token(container_name, expiry_seconds)
            if not url:
                return token
            return self.builb_container_sas_url(container_name, token)
        
        else:
            raise ValueError("Either blob_token or container_token must be True.")
    