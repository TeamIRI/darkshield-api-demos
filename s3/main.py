import boto3
import io
import json
import logging
import os
import re
import requests
import sys

# Append parent directory to PYTHON_PATH so we can import utils.py
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from setup import setup, teardown, file_mask_context_name, file_search_context_name
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget, FileTarget, NullTarget

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python main.py bucket_name')
    else:   
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
        bucket_name = sys.argv[1]
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)
        try:
            setup()
            url = 'http://localhost:8080/api/darkshield/files/fileSearchContext.mask'
            context = json.dumps({
                "fileSearchContextName": file_search_context_name,
                "fileMaskContextName": file_mask_context_name
            })

            for obj in bucket.objects.all():
                file_name = obj.key
                obj.load() # Load the metadata for this object.
                content_type = obj.meta.data.get('ContentType', 'application/octet-stream')
                # Skip prefix folders or files that were already masked.
                if content_type.startswith('application/x-directory') or file_name.startswith('masked'):
                    continue
                # For larger files, a streaming solution should be used so that the file isn't loaded
                # fully in memory before being sent to the API.
                f = obj.get()['Body'].read()
                files = {'file': (file_name, io.BytesIO(f), content_type), 'context': context}
                logging.info(f"POST: sending '{file_name}' to {url}")
                with requests.post(url, files=files, stream=True) as r:
                    if r.status_code >= 300:
                        raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")

                    folder_name = f"results/{file_name.replace('.', '_')}"
                    os.makedirs(folder_name, exist_ok=True)
                    logging.info(f"Extracting 'results.json' for '{file_name}' into '{folder_name}' folder.")
                    parser = StreamingFormDataParser(headers=r.headers)
                    # For larger files, a temporary file needs to be created and then streamed to the
                    # S3 bucket.
                    masked_file = ValueTarget()
                    parser.register('file', masked_file)
                    parser.register('results', FileTarget(f'{folder_name}/results.json'))
                    for chunk in r.iter_content():
                        parser.data_received(chunk)

                    key = f'masked/{file_name}'
                    logging.info(f"Putting masked file in '{key}'.")
                    value = masked_file.value    
                    bucket.put_object(Key=key,
                                      Body=masked_file.value)
        finally:
            teardown()
