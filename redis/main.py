import redis
import random
import json
import os
import logging
import requests
import sys



current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from requests_toolbelt import MultipartEncoder
from setup import setup, teardown, file_mask_context_name, file_search_context_name
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget, FileTarget, NullTarget
from utils import base_url


random.seed(444)

red = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)


customers = {f"customer:{random.getrandbits(32)}": i for i in (
    {
        "name": "Harry Ford",
        "email": "atlok1@gmail.com",
        "ssn": "453-23-8986",
        "phone": "321-266-2222"
    },
    {
        "name": "Sally Robin",
        "email": "atlok2@gmail.com",
        "ssn": "453-26-8483",
        "phone": "321-992-2222"
    },
    {
        "name": "Jessica Thomas",
        "email": "atlok3@gmail.com",
        "ssn": "888-23-8983",
        "phone": "888-282-2222"
    })
}

with red.pipeline() as pipe:
    for c_id, customer in customers.items():
        pipe.hmset(c_id, customer)
    pipe.execute()

list_str = red.keys()



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
        i=1
        for key in list_str:
            dict_value = red.hgetall(key)
            #new_data = {}
            json_value = json.dumps(dict_value, indent=True)
            name = "item"+str(i)+".json"
            results_name = "results"+str(i)+".json"
            process_files = [(name, 'application/json', 'redis-masked')]
            for file_name, media_type, masked_folder in process_files:
                f = json_value
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
                    parser = StreamingFormDataParser(headers=r.headers)
                    print(file_name)
                    print(results_name)
                    parser.register('file', FileTarget(f'{masked_folder}/{file_name}'))
                    parser.register('results', FileTarget(f'{masked_folder}/{results_name}'))
                    i=i+1
                    for chunk in r.iter_content(4096):
                        parser.data_received(chunk)

                    #Update redisdb with new data from masking operation

                    #my_bytes_value = ValueTarget()
                    #parser.register('file', my_bytes_value)                          
                    #for chunk in r.iter_content(4096):
                     #   parser.data_received(chunk)
                    #bson_value = my_bytes_value.value
                    #data = bson_value.decode('utf-8')
                    #new_data[key] = json.loads(data)
                    #red.hmset(key, new_data[key])
            
                    
            





    finally:
            teardown(session)
