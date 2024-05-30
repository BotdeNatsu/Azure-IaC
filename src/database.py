import os
import datetime
import pytz
from azure.cosmos import CosmosClient

class Database():
    def __init__(self):
        self.__cosmos_url = os.environ["ACCOUNT_URI_COSMOS_DB"]
        self.__cosmos_key = os.environ["ACCOUNT_KEY_COSMOS_DB"]
        self.__cosmos_database_id = os.environ["DATABASE_ID"]
        self.__cosmos_container_id = os.environ["CONTAINER_ID"]
   
    def create_client(self):
        """Azure Cosmos DB Service Authentication


        Returns:
            dict: data dictionary with the authentication object

        """
        try:
            client = CosmosClient(self.__cosmos_url, credential=self.__cosmos_key)
            return {'ok':True,'message':client}
        except Exception as e:
            return {'ok':False,'message':e}

    def create_item(self,client,hour,status_code,callcoment,image_path,guId,appCaller,appRecieverId):
        """creation of new records for log storage

        Args:
            client (objet): _description_
            hour (string): current time of the request
            status_code (int): request status code
            callcoment (string): response to the request
            image_path (string): image path in storage account
            guId (string): Id request
            appCaller (string): application that makes the call of the request
            appRecieverId (string): application that receives the call of the request

        Returns:
            dict: _description_
        """
        try:
            database = client.get_database_client(self.__cosmos_database_id)
            container = database.get_container_client(self.__cosmos_container_id)
            partition_key_value = f"{guId}"
            item = {
                "calldate": f"{hour}",
                "callstatus": status_code,
                "callcomment": callcoment,
                "image_path": f"{image_path}",
                "Guid": f"{guId}",
                "appCaller": f"{appCaller}",
                "appRecieverId": f"{appRecieverId}"
            }
            item['id'] = partition_key_value
            container.upsert_item(item)
            return {'ok':True}
        except Exception as e:
            return {'ok':False,'message':e}
        
    def get_date(self):
        """get date, current day, current year, current month from costa rica time zone

        Returns:
            dict: returns date, current day, current year, current month of the Costa Rica time zone
        """
        try:
            costa_rica_timezone = pytz.timezone('America/Costa_Rica')
            utc_now = datetime.datetime.utcnow()
            costa_rica_time = utc_now.replace(tzinfo=pytz.utc).astimezone(costa_rica_timezone)
            year = costa_rica_time.strftime("%Y")
            month = costa_rica_time.strftime("%m")
            day = costa_rica_time.strftime("%d")
            costa_rica_time = costa_rica_time.strftime('%Y-%m-%d %H:%M:%S')
            return {'ok':True,'hour_cosmos':costa_rica_time,'year':year,'month':month,'day':day }
        except Exception as e:
            return {'ok':False,'message':e}
        
