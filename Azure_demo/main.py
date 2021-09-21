import io
import json
import logging
import os
import re
import requests
import sys
import argparse
from azure.storage.blob import BlobServiceClient, ContentSettings, BlobClient, ContainerClient, __version__

AZURE = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
blob_service_client = BlobServiceClient.from_connection_string(AZURE)

# # Append parent directory to PYTHON_PATH so we can import utils.py
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from requests_toolbelt import MultipartEncoder
from setup import setup, teardown, file_mask_context_name, file_search_context_name
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget, FileTarget, NullTarget



if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    session=requests.Session()
    parser = argparse.ArgumentParser(description='Demo for Azure Blob Storage search/masking.')
    parser.add_argument('masked_container_name', type=str, help="The destination container for masked blobs.")
    parser.add_argument('container_name', type=str, help="The name of the container to be searched.")
    parser.add_argument('folder_name_or_file_path', nargs='?', type=str, default='', help="Prefix e.g.(folder1/folder2/) or full path to file folder/example.txt.")
    args = parser.parse_args()
    masked_container_name = args.masked_container_name
    container_name = args.container_name
    folder_prefix = args.folder_name_or_file_path
    if(folder_prefix != ''):
        if(folder_prefix.find('/') == -1 and folder_prefix.find('.') == -1):
            logging.info("Folder name or file path was not in correct format (folder/ or folder/example.txt)")
            exit()
    


    AZURE = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    blob_service_client = BlobServiceClient.from_connection_string(AZURE)
    container_client = blob_service_client.get_container_client(container_name)
    masked_container = blob_service_client.get_container_client(masked_container_name)
    if not masked_container.exists():
        masked_container.create_container()
    else:
        print("already exists")

    try:
        setup(session)
        url = 'http://localhost:8080/api/darkshield/files/fileSearchContext.mask'
        context = json.dumps({
            "fileSearchContextName": file_search_context_name,
            "fileMaskContextName": file_mask_context_name
        })

        for blob in container_client.list_blobs(name_starts_with=folder_prefix):

            if(not blob.name.endswith("/")):
                bytes = container_client.get_blob_client(blob).download_blob().readall()
                blob_data = bytes
                blob_settings = blob.content_settings.content_type
                my_content_settings = ContentSettings(content_type=blob_settings)
                process_files = [(blob.name, blob_settings)]

                for file_name, media_type in process_files:
                    f = blob_data
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
                        masked_file = ValueTarget()                      
                        parser.register('file', masked_file)                    
                        for chunk in r.iter_content(4096):
                            parser.data_received(chunk)
                        destination = blob.name
                        logging.info(f"putting masked file in '{destination}'.")
                        data = masked_file.value
                        source_blob_client = masked_container.get_blob_client(destination)
                        source_blob_client.upload_blob(data, blob_type="BlockBlob", overwrite=True, content_settings=my_content_settings)
                                       
    finally:
        teardown(session)


