import json
import logging
import os
import sys
import requests

# Append parent directory to PYTHON_PATH so we can import utils.py
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from bson import json_util
from setup2 import setup, teardown
from requests_toolbelt import MultipartEncoder
from requests_toolbelt.multipart import decoder
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget, FileTarget
from utils import base_url

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    session = requests.Session()
    try:
        setup(session)
        url = f'{base_url}/nosql/nosqlSearchContext.mask'

        headers_content = {
            'accept': 'multipart/form-data',
            'Content-Type': 'multipart/form-data'
            }
        data = 'context={\"nosqlSearchContextName\": \"NoSqlSearchContext\", \"nosqlMaskContextName\": \"NoSqlMaskContext\"}'
        
        context = json.dumps({
            "nosqlSearchContextName": "NoSqlSearchContext", 
            "nosqlMaskContextName": "NoSqlMaskContext"
        })
        encoder = MultipartEncoder(fields={
            'context': ('context', context, 'application/json'),
        })

        with session.post(url, data=encoder, headers={'Content-Type': encoder.content_type}) as r:
            if r.status_code >= 300:
                raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
            for line in r.iter_lines():
                print(str(line, encoding='utf-8'))


    finally:
        teardown(session=session)
    
