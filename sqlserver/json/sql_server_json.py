import argparse
import datetime
import io
import json
import logging
import os
import sys

import pyodbc
import requests

# Append parent directory to PYTHON_PATH so we can import utils.py
sys.path.append("../../")

from requests_toolbelt import MultipartEncoder
from setup import setup, teardown, file_mask_context_name, file_search_context_name
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget
from utils import base_url

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Demo for SQL Server search/masking.')
    parser.add_argument('-H', '--hostname', type=str, help="The name of the hostname hosting the SQL Server.",
                        required=False, default='localhost')
    parser.add_argument('-P', '--port', type=str,
                        help='The port of the SQL Server.', required=False, default='1433')
    parser.add_argument('-u', '--username', type=str,
                        help='The username for SQL Server.', required=True)
    parser.add_argument('-p', '--password', type=str,
                        help='The password for the given username to connect to SQL Server with.', required=True)
    parser.add_argument('-d', '--database', type=str,
                        help='The database name to connect to SQL Server with.', required=True)
    parser.add_argument('-t', '--table', type=str,
                        help='The database table name to get data from.', required=True)
    parser.add_argument('-T', '--target', type=str,
                        help='The database table name to output to.', required=True)
    parser.add_argument('-s', '--schema', type=str,
                        help='The schema name to find the table within.', required=True)
    parser.add_argument('-q', '--query', type=str,
                        help='A select portion (before FROM) of a SQL query to use.',
                        required=False, default='SELECT *')
    parser.add_argument('-b', '--batchsize', type=int,
                        help='Number of rows of data to insert into target table at a time.',
                        required=False, default=2000)
    args = parser.parse_args()
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    server = '{},{}'.format(args.hostname, args.port)
    cnxn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' +
        args.database + ';UID=' + args.username + ';PWD=' + args.password)
    cursor = cnxn.cursor()
    cursor.execute("SELECT * FROM {}.{}".format(args.schema, args.table))
    result = cursor.fetchall()
    field_names = [i[0] for i in cursor.description]
    data_types = [i[1] for i in cursor.description]
    num_fields = len(field_names)
    field_names_string = "("
    paramstring1 = ""
    paramstring2 = ":" + str(num_fields + 1)
    for w in range(num_fields):
        if w == num_fields - 1:
            field_names_string = field_names_string + field_names[w] + ")"
            paramstring1 = paramstring1 + "?"
            break
        field_names_string = field_names_string + field_names[w] + ", "
        paramstring1 = paramstring1 + "?" + ", "
    batchmaskedvalues = []
    # create new table with the same structure based on the source table.
    try:
        cursor.execute(
            "SELECT * INTO {}.{} FROM {}.{} WHERE 1 <> 1".format(args.schema, args.target, args.schema, args.table))
    except pyodbc.ProgrammingError:
        logging.warning(f"{args.target} already exists. Column layout will not be changed..")
    logging.info(f"Truncating {args.target}...")
    cursor.execute('TRUNCATE TABLE {}.{}'.format(args.schema, args.target))
    logging.info(f"Getting table info...")
    cursor.execute('{} FROM {}.{}'.format(args.query, args.schema, args.table))
    logging.info(
        f'Searching and masking {args.schema}.{args.table}... Output will be sent to {args.schema}.{args.target}.')
    s = requests.Session()
    url = f'{base_url}/searchContext.mask'
    urlfile = f'{base_url}/files/fileSearchContext.mask'
    contextfile = json.dumps({
        "fileSearchContextName": file_search_context_name,
        "fileMaskContextName": file_mask_context_name
    })
    data = cursor.fetchall()
    logging.info(f"{datetime.datetime.now()}")
    try:
        setup(s)
        logging.info(f"{datetime.datetime.now()}")
        for row_count, row in enumerate(data):
            if row_count % 200 == 0 and row_count != 0:
                logging.info(f"Searched and masked {row_count} rows.")
            rowvalues = []
            rowmaskedvalues = []
            for column_count, column in enumerate(row):
                # Assuming the JSON is only in the varbinary columns...
                if isinstance(column, bytes):
                    encoder = MultipartEncoder(fields={
                        'context': ('context', contextfile, 'application/json'),
                        'file': ('file.json', io.BytesIO(column), 'application/json')
                    })
                    with s.post(urlfile, data=encoder, stream=True,
                                headers={'Content-Type': encoder.content_type}) as r:
                        if r.status_code >= 300:
                            raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                        fileval = ValueTarget()
                        parser = StreamingFormDataParser(headers=r.headers)
                        parser.register('file', fileval)
                        for chunk in r.iter_content(chunk_size=4096):
                            parser.data_received(chunk)
                        if len(fileval.value) > 0:
                            rowmaskedvalues.append(fileval.value)
                        else:
                            rowmaskedvalues.append(column)
                # elif isinstance(column, str):
                #     encoder = MultipartEncoder(fields={
                #         'context': ('context', contextfile, 'application/json'),
                #         'file': ('file.json', io.BytesIO(bytes(column, 'utf-8')), 'application/json')
                #     })
                #     with s.post(urlfile, data=encoder, stream=True,  headers={'Content-Type': encoder.content_type}) as r:
                #         if r.status_code >= 300:
                #             raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                #         fileval = ValueTarget()
                #         parser = StreamingFormDataParser(headers=r.headers)
                #         parser.register('file', fileval)
                #         for chunk in r.iter_content(chunk_size=4096):
                #             parser.data_received(chunk)
                #         if len(fileval.value) > 0:
                #             rowmaskedvalues.append(fileval.value)
                #         else:
                #             rowmaskedvalues.append(column)
                else:
                    rowmaskedvalues.append(column)
            if column_count == num_fields - 1:
                batchmaskedvalues.append(rowmaskedvalues)
                if row_count % args.batchsize == 0 and row_count != 0:
                    logging.info(f"Sending batch of {args.batchsize} rows to target table {args.target}...")
                    cursor.executemany("""
                                   insert into {}.{} {} 
                                   values ({})""".format(args.schema, args.target, field_names_string, paramstring1),
                                       batchmaskedvalues)
                    cnxn.commit()
                    batchmaskedvalues = []
        logging.info(f"Sending last batch to target table {args.target}...")
        cursor.executemany("""
                insert into {}.{} {} 
                values ({})""".format(args.schema, args.target, field_names_string, paramstring1), batchmaskedvalues)
        cnxn.commit()
        logging.info("Complete.")
        logging.info(f"{datetime.datetime.now()}")
    finally:
        teardown(s)
