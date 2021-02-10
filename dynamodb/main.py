import argparse
import boto3
import io
import json
import logging
import os
import re
import requests
import simplejson as json
import sys

from botocore import exceptions

# Append parent directory to PYTHON_PATH so we can import utils.py
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from setup import create_table, populate_test_data, setup, teardown, file_mask_context_name, file_search_context_name
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget, FileTarget, NullTarget

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    parser = argparse.ArgumentParser(description='Demo for DynamoDB table search/masking.')
    parser.add_argument('url', type=str, help='The DynamoDB url.')
    parser.add_argument('-p', '--profile', metavar='name', type=str, 
                        help='The name of AWS profile to use for the connection (otherwise the default is used).')
    
    args = parser.parse_args()
    endpoint_url = args.url
    table_name = 'darkshield-test'
    masked_table_name = f'{table_name}-masked'
    if args.profile:
        session = boto3.Session(profile_name=args.profile)
    else:
        session = boto3.Session()

    dynamodb = session.resource('dynamodb', endpoint_url=endpoint_url)

    # Create test table and load test data if it doesn't already exist
    try:
        table = create_table(dynamodb, table_name)
        populate_test_data(table)
    except exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            logging.info(f'Using existing "{table_name}"" table.')
            table = dynamodb.Table('darkshield-test')
        else:
            raise e

    # Create or clear the masked table.
    logging.info(f'Deleting {masked_table_name} if it does not exist...')
    try:
        masked_table = dynamodb.Table(masked_table_name)
        masked_table.delete()
        masked_table.wait_until_not_exists()
        logging.info(f'Deleted {masked_table_name}.')
    except exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logging.info(f'{masked_table_name} does not exist.')
        else:
            raise e
    
    masked_table = create_table(dynamodb, masked_table_name)

    try:
        setup()
        url = 'http://localhost:8080/api/darkshield/files/fileSearchContext.mask'
        context = json.dumps({
            "fileSearchContextName": file_search_context_name,
            "fileMaskContextName": file_mask_context_name
        })

        os.makedirs('results', exist_ok=True)

        scan_kwargs = { # Add any filters here.
            'ConsistentRead': True # Slower, but less likely to miss an item that was added recently.
        }
        done = False
        start_key = None
        batch_index = 1
        # Scan over the entire table in paginated batches until the end is reached.
        # This code will read the table sequentially, however parallel processing is possible 
        # for faster scans, see 
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.scan
        while not done:
            if start_key:
                scan_kwargs['ExclusiveStartKey'] = start_key
            response = table.scan(**scan_kwargs)
            items = response.get('Items', [])
            batch_name = f'batch{batch_index}'
            batch_index += 1
            files = {'file': (batch_name, json.dumps(items), 'application/json'), 'context': context}
            logging.info(f"POST: sending '{batch_name}' to {url}")
            with requests.post(url, files=files, stream=True) as r:
                if r.status_code >= 300:
                    raise Exception(f"Failed {batch_name} with status {r.status_code}:\n\n{r.json()}")

                results_file_name = f'{batch_name}-results.json'
                logging.info(f"Extracting '{results_file_name}' into the 'results' folder.")
                parser = StreamingFormDataParser(headers=r.headers)
                masked_batch = ValueTarget()
                parser.register('file', masked_batch)
                parser.register('results', FileTarget(f'results/{results_file_name}'))
                for chunk in r.iter_content():
                    parser.data_received(chunk)

            masked_batch = json.loads(masked_batch.value)
            # The batch writer will automatically handle buffering and sending items in batches.
            # In addition, the batch writer will also automatically handle any unprocessed items and resend them as needed.
            with masked_table.batch_writer() as batch:
                for item in masked_batch:
                    batch.put_item(Item=item)
            
            start_key = response.get('LastEvaluatedKey', None)
            done = start_key is None
    finally:
        teardown()
