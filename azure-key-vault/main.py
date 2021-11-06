import json
import logging
import os
import sys

import requests

# Append parent directory to PYTHON_PATH so we can import utils.py
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from requests_toolbelt import MultipartEncoder
from setup import setup, teardown, file_mask_context_name, file_search_context_name
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget
from utils import base_url

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    session = requests.Session()
    try:
        setup(session)
        url = f'{base_url}/files/fileSearchContext.mask'
        context = json.dumps({
            "fileSearchContextName": file_search_context_name,
            "fileMaskContextName": file_mask_context_name
        })
        process_files = [('test.json', 'application/json', 'json-masked-key-vault'),
                         ('test.xml', 'application/xml', 'xml-masked-key-vault')]
        for file_name, media_type, masked_folder in process_files:
            with open(file_name, 'rb') as f:
                os.makedirs(masked_folder, exist_ok=True)
                encoder = MultipartEncoder(fields={
                    'context': ('context', context, 'application/json'),
                    'file': (file_name, f, media_type)
                })
                logging.info(f"POST: sending '{file_name}' to {url}")
                with session.post(url, data=encoder, stream=True,
                                  headers={'Content-Type': encoder.content_type}) as r:
                    if r.status_code >= 300:
                        raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                    logging.info(f"Extracting '{file_name}' and 'results.json' into {masked_folder}.")
                    parser = StreamingFormDataParser(headers=r.headers)
                    parser.register('file', FileTarget(f'{masked_folder}/{file_name}'))
                    parser.register('results', FileTarget(f'{masked_folder}/results.json'))
                    for chunk in r.iter_content(4096):
                        parser.data_received(chunk)
    finally:
        teardown(session)
