
import json
import logging
import os
import io
import sys
import requests
import uncurl


current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from requests_toolbelt import MultipartEncoder
from setup import setup, teardown, file_mask_context_name, file_search_context_name
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget
from utils import base_url



session = requests.Session()
session.auth = ("admin", "admin")
session.put("https://localhost:9200/my-first-index", verify=False)
session.put("https://localhost:9200/my-first-index/_doc/1", 
data='{    \"id\": \"5d35ed837a0cf8f1691ebedc\",    \"name\": \"Kathy Wynn\", '+ 
'  \"gender\": \"female\",    \"email\": \"kathy@duoflex.com\", '+ 
'  \"phone\": \"+1 (843) 400-3871\",    \"registered\": \"2018-03-22T12:55:39 +04:00\", ' + 
'  \"friends\": [      {        \"id\": 0,        \"name\": \"Thomas Duffy\"      }, ' + 
'   {        \"id\": 1,        \"name\": \"Jami Myers\"      }, '+ 
'   {        \"id\": 2,        \"name\": \"Alissa Justice\"      }    ], ' + 
'   \"greeting\": \"Hello, Kathy Wynn! You have a new message in the following email: kathy@duoflex.com.\"}',
    headers={        "Content-Type": "application/json"   },   cookies={},    
    auth=('admin', 'admin'),    verify=False)

result = session.get(
    "https://localhost:9200/my-first-index/_doc/1", verify=False)

session.close

if __name__ == "__main__":
    logging.basicConfig(
        format='%(levelname)s: %(message)s', level=logging.INFO)
    session = requests.Session()
   
    
    try:
        url = f'{base_url}/files/fileSearchContext.mask'
        context = json.dumps({
        "fileSearchContextName": "FileSearchContext",
        "fileMaskContextName": "FileMaskContext"
        })
        setup(session)
       
        folder_name = f"masked_folder"
        
        os.makedirs(folder_name, exist_ok=True)
        encoder = MultipartEncoder(fields={
            'context':  ('context', context, 'application/json'),
            'file': ('document.json', io.BytesIO(result.text.encode()), 'application/json')
        })

        with session.post(url, data=encoder, stream=True,  headers={'Content-Type': encoder.content_type}) as r:
            if r.status_code >= 300:
                raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
            logging.info(f"Extracting 'results.json' for 'document.json' into '{folder_name}' folder.")
            parser = StreamingFormDataParser(headers=r.headers)

            parser.register('file', FileTarget(f'{folder_name}/document.json'))
            parser.register('results', FileTarget(f'{folder_name}/results.json'))
            for chunk in r.iter_content(4096):
                parser.data_received(chunk)

       
      
    finally:
        teardown(session)

session = requests.Session()
session.auth = ("admin", "admin")
session.delete("https://localhost:9200/my-first-index/_doc/1", verify=False)
session.delete("https://localhost:9200/my-first-index", verify=False)
session.close()
