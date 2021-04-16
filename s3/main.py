import argparse
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
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    session=requests.Session()
    parser = argparse.ArgumentParser(description='Demo for S3 bucket search/masking.')
    parser.add_argument('bucket_name_or_url', type=str, help="The name of the bucket, or the s3 url of the object (starting with 's3://').")
    parser.add_argument('-p', '--profile', metavar='name', type=str, 
                        help='The name of AWS profile to use for the connection (otherwise the default is used).')

    args = parser.parse_args()
    if args.profile:
        session = boto3.Session(profile_name=args.profile)
    else:
        session = boto3.Session()

    s3 = session.resource('s3')
    bucket_name = args.bucket_name_or_url
    prefix = ''
    if bucket_name.startswith('s3://'):
        split = bucket_name[5:].split('/', 1)
        if len(split) == 2:
            bucket_name, prefix = split
        else:
            bucket_name = split[0]
    
    bucket = s3.Bucket(bucket_name)
    try:
        setup()
        url = 'http://localhost:8080/api/darkshield/files/fileSearchContext.mask'
        context = json.dumps({
            "fileSearchContextName": file_search_context_name,
            "fileMaskContextName": file_mask_context_name
        })
        if prefix:
            logging.info(f"Filtering on prefix '{prefix}'...")
            objects = bucket.objects.filter(Prefix=prefix)
        else:
            logging.info('Extracting all objects from bucket...')
            objects = bucket.objects.all()
        
        for obj in objects:
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
            with session.post(url, files=files, stream=True) as r:
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
                for chunk in r.iter_content(4096):
                    parser.data_received(chunk)

                key = f'masked/{file_name}'
                logging.info(f"Putting masked file in '{key}'.")
                value = masked_file.value    
                bucket.put_object(Key=key, Body=masked_file.value)
    finally:
        teardown()
