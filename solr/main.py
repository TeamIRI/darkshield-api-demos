from urllib.request import urlopen
import argparse
import json
import logging
import os
import sys
import io

import requests

# Append parent directory to PYTHON_PATH so we can import utils.py
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from setup import setup, teardown, file_mask_context_name, file_search_context_name
from requests_toolbelt import MultipartEncoder
from utils import base_url
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget


def main(args):
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    s = requests.Session()
    # url = f'{base_url}/searchContext.mask'
    urlfile = f'{base_url}/files/fileSearchContext.mask'
    json_post = f'http://{args.host}:{args.port}/solr/{args.collection_name}/update'
    contextfile = json.dumps({
        "fileSearchContextName": file_search_context_name,
        "fileMaskContextName": file_mask_context_name
    })
    try:
        setup(s)
        connection = urlopen(f'http://{args.host}:{args.port}/solr/{args.collection_name}/select?indent=true&q.op=OR'
                             f'&rows={args.rows}'
                             f'&q={args.query}')
        response = json.load(connection)
        logging.info(f"{response['response']['numFound']} documents found.")

        for count, document in enumerate(response['response']['docs']):
            encoder = MultipartEncoder(fields={
                'context': ('context', contextfile, 'application/json'),
                'file': ('file.json', io.BytesIO(json.dumps(document).encode()), 'application/json')
            })
            logging.info(f'Sending document {count + 1} to DarkShield API...')
            with s.post(urlfile, data=encoder, stream=True, headers={'Content-Type': encoder.content_type}) as r:
                if r.status_code >= 300:
                    raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                fileval = ValueTarget()
                s_parser = StreamingFormDataParser(headers=r.headers)
                s_parser.register('file', fileval)
                for chunk in r.iter_content(chunk_size=4096):
                    s_parser.data_received(chunk)
                if len(fileval.value) > 0:
                    logging.info(f'Sending masked document {count + 1} to Solr to update data...')
                    with s.post(json_post, json={'add': {'doc': json.loads(fileval.value.decode())}}) as r2:
                        if r2.status_code >= 300:
                            raise Exception(f"Solr post failed with status {r2.status_code}:\n")
                        logging.info(f'Successfully updated masked document {count + 1} of '
                                     f'collection {args.collection_name}...')
    finally:
        teardown(s)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Demo for Solr collection search/masking.')
    parser.add_argument('--collection_name', type=str, help="The collection to search and mask.", required=False,
                        default='test')
    parser.add_argument('--host', type=str, help="The host of Solr.", default='localhost', required=False)
    parser.add_argument('--port', type=str, default='8983',
                        help="The port of Solr.", required=False)
    parser.add_argument('--query', type=str, default='*',
                        help="The search query to use.", required=False)
    parser.add_argument('--rows', type=str, default='100',
                        help="The number of rows to limit query results to.", required=False)
    arguments = parser.parse_args()
    main(arguments)
