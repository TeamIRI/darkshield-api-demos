"""Demonstrates how to connect to Cloud Bigtable, put some data into a table, send to the DarkShield API, and
put the masked results back into the table.

Prerequisites:

- Create a Cloud Bigtable cluster.
  https://cloud.google.com/bigtable/docs/creating-cluster
- Set your Google Application Default Credentials.
  https://developers.google.com/identity/protocols/application-default-credentials
"""

import argparse
import datetime
import logging
import json
import requests
import sys
import os

# Append parent directory to PYTHON_PATH so we can import utils.py
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from setup import setup, teardown, file_mask_context_name, file_search_context_name

from google.cloud import bigtable
from google.cloud.bigtable import column_family


def main(project_id, instance_id, table_id):
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    s = requests.Session()
    url = 'http://localhost:8080/api/darkshield/searchContext.mask'
    urlfile = 'http://localhost:8080/api/darkshield/files/fileSearchContext.mask'
    contextfile = json.dumps({
        "fileSearchContextName": file_search_context_name,
        "fileMaskContextName": file_mask_context_name
    })
    try:
        setup(s)
        client = bigtable.Client(project=project_id, admin=True)
        instance = client.instance(instance_id)
        logging.info('Creating the {} table.'.format(table_id))
        table = instance.table(table_id)
        logging.info('Creating column family cf1 with Max Version GC rule...')
        max_versions_rule = column_family.MaxVersionsGCRule(2)
        column_family_id = 'cf1'
        column_families = {column_family_id: max_versions_rule}
        if not table.exists():
            table.create(column_families=column_families)
        else:
            logging.info("Table {} already exists.".format(table_id))
        logging.info('Writing some messages to the table.')
        greetings = ['Hello, my name is John Doe and I am waiting to be found.', 'The email is johndoe@gmail.com',
                     'The credit card number is 6011434323278222.']
        rows = []
        column = 'message'.encode()
        for i, value in enumerate(greetings):
            row_key = 'message{}'.format(i).encode()
            row = table.direct_row(row_key)
            row.set_cell(column_family_id,
                         column,
                         value,
                         timestamp=datetime.datetime.utcnow())
            rows.append(row)
        table.mutate_rows(rows)
        for i, value in enumerate(greetings):
            row_key = 'message{}'.format(i).encode()
            row = table.read_row(row_key)
            cell = row.cells[column_family_id][column][0]
            cell_value = cell.value.decode('utf-8')
            logging.info('Read value \'{}\' from table...'.format(cell_value))
            with s.post(url, json={"searchContextName": "SearchContext", "maskContextName": "MaskContext", "text": "{}".format(cell_value)}) as r:
                if r.status_code >= 300:
                    raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                logging.info('Putting masked response text \'{}\' into table...'.format(r.json()['maskedText']))
                write_row = table.row(row_key)
                write_row.set_cell(column_family_id,
                                   column,
                                   r.json()['maskedText'],
                                   timestamp=datetime.datetime.utcnow())
    finally:
        teardown(s)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('project_id', help='Your Cloud Platform project ID.')
    parser.add_argument(
        'instance_id', help='ID of the Cloud Bigtable instance to connect to.')
    parser.add_argument(
        '--table',
        help='Table to create and destroy.',
        default='Hello-Bigtable')
    args = parser.parse_args()
    main(args.project_id, args.instance_id, args.table)
