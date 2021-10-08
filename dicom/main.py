import json
import logging
import os
import requests
import sys

# Append parent directory to PYTHON_PATH so we can import utils.py
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from requests_toolbelt import MultipartEncoder
from setup import setup, teardown, file_mask_context_name, file_search_context_name, file_mask_context_name_blackout
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    masked_folder = "masked"
    session = requests.Session()
    try:
        setup(session)
        url = 'http://localhost:8080/api/darkshield/files/fileSearchContext.mask'
        urltext = 'http://localhost:8080/api/darkshield/searchContext.mask'
        context = json.dumps({
            "fileSearchContextName": file_search_context_name,
            "fileMaskContextName": file_mask_context_name
        })
        # a separate context to blackout portions of pixel data within a DICOM file known to have burned-in text.
        blackout_context = json.dumps({
            "fileSearchContextName": file_search_context_name,
            "fileMaskContextName": file_mask_context_name_blackout
        })
        
        directory = 'DICOM_FILESYSTEM'
        root_directory = './'
        for dir_, _, files in os.walk(directory):
            for file_name in files:
                rel_dir = os.path.relpath(dir_, root_directory)
                rel_file = os.path.join(rel_dir, file_name)
                with open(rel_file, 'rb') as f:
                    media_type = ''
                    if file_name.endswith('.csv'):
                        media_type = 'text/csv'
                    elif file_name.endswith('.dcm'):
                        media_type = 'application/dicom'
                    if '1002.000000-NA-53238' in rel_dir: # This scan is known to have burned-in annotations.
                        encoder = MultipartEncoder(fields={
                        'context': ('context', blackout_context, 'application/json'),
                        'file': (rel_file, f, media_type)
                    })
                    else:
                        encoder = MultipartEncoder(fields={
                        'context': ('context', context, 'application/json'),
                        'file': (rel_file, f, media_type)
                    })
                    new_rel_dir = ''
                    new_rel_file = ''
                    with session.post(urltext, json={"searchContextName": "SearchContext", "maskContextName":
                        "MaskContext", "text": "{}".format(rel_dir)}) as r:
                        if r.status_code >= 300:
                            raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                        new_rel_dir = r.json()['maskedText']
                        new_rel_file = os.path.join(new_rel_dir, file_name)
                        logging.info('Masked directory name.')
                    new_directory = f'{os.path.join(masked_folder, new_rel_dir)}'
                    new_file = f'{os.path.join(masked_folder, new_rel_file)}'
                    new_results = f'{os.path.join(masked_folder, new_rel_file)}_results.json'
                    os.makedirs(new_directory, exist_ok=True)
                    logging.info(f"POST: sending '{file_name}' to {url}")
                    with session.post(url, data=encoder, stream=True, headers={'Content-Type': encoder.content_type}) as r:
                        if r.status_code >= 300:
                            raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                        logging.info(f"Extracting '{file_name}' and 'results.json' into {os.path.join(masked_folder, new_rel_dir)}.")
                        parser = StreamingFormDataParser(headers=r.headers)
                        parser.register('file', FileTarget(new_file))
                        parser.register('results', FileTarget(new_results))
                        for chunk in r.iter_content(4096):
                            parser.data_received(chunk)
    finally:
        teardown(session)
