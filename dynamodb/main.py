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

from setup import create_table, delete_table, populate_test_data, setup, teardown, file_mask_context_name, file_search_context_name
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget, FileTarget, NullTarget

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    parser = argparse.ArgumentParser(description='Demo for DynamoDB table search/masking.')
    parser.add_argument('table', type=str, help="The source table name to use for the search. If it doesn't exist, it will be created.")
    parser.add_argument('-d', '--delete-existing', action='store_true', help='Delete the source and target tables before running the demo.')
    parser.add_argument('-p', '--profile', metavar='name', type=str, help='The name of AWS profile to use for the connection (otherwise the default is used).')
    parser.add_argument('-t', '--target', metavar='name', type=str, help="The target table name (by default, an update is performed on the source table).")

    exclusive_group = parser.add_mutually_exclusive_group()
    exclusive_group.add_argument('-e', '--endpoint', metavar='name', type=str, help='Specify the dynamodb endpoint.')
    exclusive_group.add_argument('-r', '--region', metavar='name', type=str, help='The region name (otherwise the default for the profile is used).')
    
    args = parser.parse_args()
    table_name = args.table
    target_table_name = args.target or table_name

    session = boto3.Session(profile_name=args.profile)
    if args.endpoint:
        dynamodb = session.resource('dynamodb', endpoint_url=args.endpoint)
    elif args.region:
        dynamodb = session.resource('dynamodb', endpoint_url=f'https://dynamodb.{args.region}.amazonaws.com')
    else:   
        dynamodb = session.resource('dynamodb')

    table = dynamodb.Table(table_name)
    target_table = dynamodb.Table(target_table_name)

    if args.delete_existing:
        delete_table(table)
        if table_name != target_table_name:
            delete_table(target_table)

    scan_kwargs = { # Add any filters here.
        'ConsistentRead': True # Slower, but less likely to miss an item that was added recently.
    }

    # Try to scan the source table, if it doesn't exist create one and populate it with test data. If it does exist
    # and has no data, populate it with test data.
    try:
        response = table.scan(**scan_kwargs)
        items = response.get('Items', []) 
        if not items:
            logging.info(f"'{table_name}' is empty, populating with test data...")
            populate_test_data(table)
            response = table.scan(**scan_kwargs)
            items = response.get('Items', [])  
    except exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logging.info(f"'{table_name}' does not exist, creating...")
            table = create_table(dynamodb, table_name)
            logging.info('Populating test data...')
            populate_test_data(table)
            response = table.scan(**scan_kwargs)
            items = response.get('Items', [])  
        else:
            raise e

    if table_name != target_table_name:
        logging.info(f"Checking if '{target_table_name}' exists...")
        try:
            target_table.load()
        except exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logging.info(f"'{target_table_name}' does not exist, creating...")
                target_table = create_table(dynamodb, target_table_name)
    try:
        setup()
        url = 'http://localhost:8080/api/darkshield/files/fileSearchContext.mask'
        context = json.dumps({
            "fileSearchContextName": file_search_context_name,
            "fileMaskContextName": file_mask_context_name
        })

        os.makedirs('results', exist_ok=True)

        done = False
        batch_index = 1
        # Scan over the entire table in paginated batches until the end is reached.
        # This code will read the table sequentially, however parallel processing is possible 
        # for faster scans, see 
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.scan
        while not done:
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
            with target_table.batch_writer() as batch:
                for item in masked_batch:
                    batch.put_item(Item=item)
            
            start_key = response.get('LastEvaluatedKey', None)
            done = start_key is None
            scan_kwargs['ExclusiveStartKey'] = start_key
            if not done:
                response = table.scan(**scan_kwargs)
                items = response.get('Items', [])
    finally:
        teardown()
