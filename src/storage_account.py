import os
from azure.storage.blob import BlobServiceClient
import uuid
import logging

class DataLake():
    def __init__(self):
        self.__storage_name = os.environ["STORAGE_ACCOUNT_NAME"]
        self.__storage_key = os.environ["STORAGE_ACCOUNT_KEY"]
           
    def upload_to_azure_blob(self,year,month,day,path1,path2,file_name,file):
        """save the image to the storage account container and subfolder

        Args:
            year (string): current year of the request
            month (string): current month of the request
            day (string): current day of the request
            tag_name (string): classification label returned by the Azure custom vision AI model
            file_name (string): File name
            file (bytes): File in bytes

        Returns:
            dict: data dictionary with success classifier, unique id in storage account and saved file path
        """
        try:
            
            self.__blob_service = BlobServiceClient(account_url=f"https://{self.__storage_name}.blob.core.windows.net",credential=self.__storage_key)
            target_container_name = "bronce-zone"
            target_container_client = self.__blob_service.get_container_client(target_container_name)
            if not target_container_client.exists():
                target_container_client.create_container()
            new_guid = uuid.uuid4()
            container_client = self.__blob_service.get_container_client(target_container_name)
            blob_client = container_client.get_blob_client(f"/{year}/{month}/{day}/{path1}/{path2}/{new_guid}/{file_name}")
            blob_client.upload_blob(file,overwrite=True)
            return {
                'ok':True,
                'guid':str(new_guid),
                'path':f'https://{self.__storage_name}.blob.core.windows.net/{target_container_name}/{year}/{month}/{day}/{path1}/{path2}/{new_guid}/{file_name}'
                }
        except Exception as e:
            logging.error(e)
            return {'ok':False,'return':e}
      