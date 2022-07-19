import argparse
import logging
import pysftp
import os
import requests
import sys
import json
import mimetypes


# Append parent directory to PYTHON_PATH so we can import utils.py
from requests_toolbelt import MultipartEncoder

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from setup import setup, teardown, file_mask_context_name, file_search_context_name
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget
from utils import base_url

maskedFolder = "masked"


def send_file_to_darkshield_api(file_name, contexts, the_URL, theSession):
    base_name = os.path.basename(file_name)
    with open(file_name, 'rb') as f:
        logging.info(f"POST: sending '{base_name}' to {the_URL}")
        media_type = mimetypes.guess_type(file_name)[0]
        encoder = MultipartEncoder(fields={
            'context': ('context', contexts, 'application/json'),
            'file': (file_name, f, media_type)
        })
        os.makedirs(maskedFolder, exist_ok=True)
        logging.info(f"POST: sending '{file_name}' to {the_URL}")
        with theSession.post(the_URL, data=encoder, stream=True,
                             headers={'Content-Type': encoder.content_type}) as r:
            if r.status_code >= 300:
                raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
            os.makedirs(maskedFolder, exist_ok=True)
            logging.info(f"Extracting '{baseFileName}' and 'results.json' into {maskedFolder}.")
            formParser = StreamingFormDataParser(headers=r.headers)
            formParser.register('file', FileTarget(f'{maskedFolder}/{baseFileName}'))
            formParser.register('results', FileTarget(f'{maskedFolder}/results.json'))
            for chunk in r.iter_content(4096):
                formParser.data_received(chunk)
    os.remove(file_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Demo for accessing files through SFTP and searching + masking with the IRI DarkShield API.')
    parser.add_argument('-H', '--hostname', type=str, help="The hostname to access.",
                        required=True)
    parser.add_argument('-u', '--username', type=str,
                        help='The username for the hostname.', required=True)
    parser.add_argument('-p', '--password', type=str,
                        help='The password for the hostname.', required=True)
    parser.add_argument('-r', '--remotepath', type=str,
                        help='The path of a file on the remote hostname.', required=True)
    args = parser.parse_args()
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    session = requests.Session()
    Hostname = args.hostname
    Username = args.username
    Password = args.password
    remoteFile = args.remotepath
    try:
        setup(session)
        url = f'{base_url}/files/fileSearchContext.mask'
        context = json.dumps({
            "fileSearchContextName": file_search_context_name,
            "fileMaskContextName": file_mask_context_name
        })
        with pysftp.Connection(host=Hostname, username=Username, password=Password) as sftp:
            logging.info("Connection successfully established ... ")
            # Use get method to download a file
            sftp.get(remoteFile)
            baseFileName = os.path.basename(remoteFile)
            send_file_to_darkshield_api(baseFileName, context, url, session)
    finally:
        teardown(session)
