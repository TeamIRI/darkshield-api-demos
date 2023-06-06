
import requests
import json
import logging
import os
import sys

# Append parent directory to PYTHON_PATH so we can import utils.py
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from requests_toolbelt import MultipartEncoder
from setup import setup, teardown, file_mask_context_name, file_search_context_name
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget, FileTarget
from utils import base_url

class Darkshield:


    
    def call_darkshield(file_path, filename):
        session = requests.Session()
        try:
            setup(session)
            url = f'{base_url}/files/fileSearchContext.mask'
            context = json.dumps({
                "fileSearchContextName": file_search_context_name,
                "fileMaskContextName": file_mask_context_name
            })

            process_files = [(file_path, filename)]

            for file_name, masked_folder in process_files:
                encoder = MultipartEncoder(fields={
                    'context': ('context', context, 'application/json'),
                    'file': (file_name, open(file_path, 'rb'))
                })
                os.makedirs("results/"+masked_folder, exist_ok=True)
                logging.info(f"POST: sending '{file_name}' to {url}")
                with session.post(url, data=encoder, stream=True,
                            headers={'Content-Type': encoder.content_type}) as r:
                    if r.status_code >= 300:
                        raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                    logging.info(f"Extracting '{file_name}' and 'results.json' into {masked_folder}.")
                    parser = StreamingFormDataParser(headers=r.headers)
                    parser.register('file', FileTarget(file_path))
                    parser.register('results', FileTarget(f'results/{masked_folder}/results.json'))
                    for chunk in r.iter_content(4096):
                        parser.data_received(chunk)
        finally:
            teardown(session)
        