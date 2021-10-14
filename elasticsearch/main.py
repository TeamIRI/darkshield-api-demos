from datetime import datetime
from elasticsearch import Elasticsearch
import json
import logging
import os
import requests
import sys
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from setup import setup, teardown
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget, FileTarget

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    session = requests.Session()
    url = 'http://localhost:8080/api/darkshield/files/fileSearchContext.mask'
    context = json.dumps({
        "fileSearchContextName": "FileSearchContext",
        "fileMaskContextName": "FileMaskContext"
    })
    setup(session)
    try:
        es = Elasticsearch()
        logging.info('Connected to Elasticsearch.\nLoading two JSON documents into test-index.')
        with open('data.json') as f:
            doc = json.loads(f.read())
        res = es.index(index="test-index", id=0, document=doc)
        with open('data_2.json') as f:
            doc = json.loads(f.read())
        res = es.index(index="test-index", id=1, document=doc)
        if res['result'] == 'created':
            logging.info('Successfully inserted two JSON documents into test-index with ids of 0 and 1.')
        es.indices.refresh(index="test-index")
        res = es.search(index="test-index", query={"match_all": {}})
        logging.info('Searching test-index...')
        logging.info("Got %d Hits:" % res['hits']['total']['value'])
        os.makedirs('results', exist_ok=True)
        logging.info('Processing data in test-index...')
        for count, hit in enumerate(res['hits']['hits']):
            files = {'file': ('document.json', json.dumps(hit["_source"]), 'application/json'),
                     'context': context}
            logging.info(f"POST: sending document with id {hit['_id']} to {url}")
            with session.post(url, files=files, stream=True) as r:
                if r.status_code >= 300:
                    raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                logging.info(f"Placing results into 'results/results{count}.json'.")
                parser = StreamingFormDataParser(headers=r.headers)
                output = ValueTarget()
                parser.register('file', output)
                parser.register('results', FileTarget(f'results/results{count}.json'))
                for chunk in r.iter_content(4096):
                    parser.data_received(chunk)
            logging.info('Sending masked result to test-index-masked.')
            res = es.index(index="test-index-masked", id=count+1, document=json.loads(output.value))
        es.indices.refresh(index="test-index-masked")
        logging.info('Searching test-index-masked to display masked results...')
        res = es.search(index="test-index-masked", query={"match_all": {}})
        logging.info("Got %d masked Hits:" % res['hits']['total']['value'])
        for count, hit in enumerate(res['hits']['hits']):
            logging.info(f'The masked result in test-index-masked at id {hit["_id"]} is:\n{hit["_source"]}')
        logging.info("Completed Elasticsearch demo.")
    finally:
        logging.info('Destroying search and mask contexts...')
        teardown(session)
