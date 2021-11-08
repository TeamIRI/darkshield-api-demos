from azure.cosmos import exceptions, CosmosClient, PartitionKey
import azure.cosmos.documents as doc
import json
import os
import logging
import requests
import sys

# Append parent directory to PYTHON_PATH so we can import utils.py
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from requests_toolbelt import MultipartEncoder
from setup import setup, teardown, file_mask_context_name, file_search_context_name
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget, FileTarget, NullTarget
from utils import base_url


f = open("credentials.json", 'r')
json_creds = json.loads(f.read())
f.close()
container_name = json_creds["InputContainer"]
mask_container_name = json_creds["OutputContainer"]
database_name = json_creds["Database"]
COSMOS_URL = json_creds["CosmosURL"]
COSMOS_KEY = json_creds["CosmosKey"]


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    session = requests.Session()
    client = CosmosClient(COSMOS_URL, credential=COSMOS_KEY)
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)
    database_client = client.get_database_client(database_name)
    container_client = database.get_container_client(container_name)
    mask_container_client = database.get_container_client(mask_container_name)
    try:
        mask_container = database.create_container_if_not_exists(
            id=mask_container_name, partition_key=PartitionKey(path="/mask")
        )
    except exceptions.CosmosResourceExistsError:
        mask_container = database.get_container_client(mask_container_name)

    try:
        setup(session)
        url = f'{base_url}/files/fileSearchContext.mask'
        context = json.dumps({
            "fileSearchContextName": file_search_context_name,
            "fileMaskContextName": file_mask_context_name
        })
      
        for item in container.query_items(
                query='SELECT * FROM Items',
                enable_cross_partition_query=True):
            
        

            process_files = [('item.json', 'application/json')]
            for file_name, media_type in process_files:
                f = json.dumps(item, indent=True)
                encoder = MultipartEncoder(fields={
                    'context': ('context', context, 'application/json'),
                    'file': (file_name, f, media_type)
                })
                logging.info(f"POST: sending '{file_name}' to {url}")
                with session.post(url, data=encoder, stream=True,
                                    headers={'Content-Type': encoder.content_type}) as r:
                    if r.status_code >= 300:
                        raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                    parser = StreamingFormDataParser(headers=r.headers)
                    my_bytes_value = ValueTarget()
                    parser.register('file', my_bytes_value)                          
                    for chunk in r.iter_content(4096):
                        parser.data_received(chunk)
                    bson_value = my_bytes_value.value
                    data = json.loads(bson_value.decode('utf-8'))
                    mask_container.upsert_item(data)
                   
    finally:
        teardown(session)
            
    
           
  