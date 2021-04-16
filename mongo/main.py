import io
import json
import logging
import os
import pymongo
import re
import requests
import sys

# Append parent directory to PYTHON_PATH so we can import utils.py
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from setup import setup, teardown
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget, FileTarget

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    session=requests.Session()
    url = 'http://localhost:8080/api/darkshield/files/fileSearchContext.mask'
    context = json.dumps({
        "fileSearchContextName": "FileSearchContext",
        "fileMaskContextName": "FileMaskContext"
    })
    try:
        with pymongo.MongoClient("localhost", 27017) as client:
            setup(session)
            db = client.darkshield
            coll = db.data
            if coll.estimated_document_count() == 0:
                logging.info("darkshield.data is empty. Loading 'data.json'...")
                with open('data.json') as f:
                    data = json.loads(f.read())
                    coll.insert_one(data)
            out_coll = db.masked
            logging.info('Dropping darkshield.masked collection...')
            out_coll.drop()

            logging.info('Loading Mongo data from darkshield.data...')
            data = coll.find({})
            os.makedirs('results', exist_ok=True)

            for index, document in enumerate(data, 1):
                files = {'file': ('document.json', json.dumps(document), 'application/json'), 
                        'context': context}
                logging.info(f"POST: sending document {index} to {url}")
                with session.post(url, files=files, stream=True) as r:
                    if r.status_code >= 300:
                        raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")

                    logging.info(f"Placing results into 'results/results{index}.json'.")
                    parser = StreamingFormDataParser(headers=r.headers)
                    output = ValueTarget()
                    parser.register('file', output)
                    parser.register('results', FileTarget(f'results/results{index}.json'))
                    for chunk in r.iter_content(4096):
                        parser.data_received(chunk)

                logging.info(f"Inserting masked document {index} into darkshield.masked...")
                out_coll.insert_one(json.loads(output.value))
    finally:
        teardown(session)
