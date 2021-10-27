import pyodbc
import argparse
import logging
import requests
import json
import sys
import os
import datetime

# Append parent directory to PYTHON_PATH so we can import utils.py
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from setup import setup, teardown, file_mask_context_name, file_search_context_name


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Demo for SQL Server search/masking. This demonstrates an '
                                                 'alternative method of processing data from the database, '
                                                 'putting all of the values together into one string to reduce the '
                                                 'number of requests needed to send to the DarkShield '
                                                 'API. The reason this is useful is because each request sent '
                                                 'inherently has some latency, so putting the same data into one big '
                                                 'request is more efficient. However, all columns should be '
                                                 'text-based (no Blobs) if using this demo.')
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
                        help='A select portion (before the FROM clause) of a SQL query to use.',
                        required=False, default='SELECT *')
    parser.add_argument('-a', '--rowsep', type=str,
                        help='Unique string to separate rows by. This string should not be present in the data '
                             'values.',
                        required=False, default='\n')
    parser.add_argument('-b', '--colsep', type=str,
                        help='Unique string to separate columns by. This string should not be present in the data '
                             'values.',
                        required=False, default='|')
    parser.add_argument('-S', '--startrow', type=int,
                        help='Start row of data to be processed. If not specified, the whole table will be processed '
                             'starting from the first row.',
                        required=False, default=0)
    parser.add_argument('-E', '--endrow', type=int,
                        help='End row of data to be processed. If not specified, the whole table will be processed '
                             'starting from the first row.',
                        required=False, default=0)
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
        cursor.execute("SELECT * INTO {}.{} FROM {}.{} WHERE 1 <> 1".format(args.schema, args.target, args.schema, args.table))
    except pyodbc.ProgrammingError:
        logging.warning(f"{args.target} already exists. Column layout will not be changed..")
    logging.info(f"Truncating {args.target}...")
    cursor.execute('TRUNCATE TABLE {}.{}'.format(args.schema, args.target))
    logging.info(f"Getting table info...")
    if 0 < args.startrow < args.endrow and args.endrow > 0:
        cursor.execute(
            "SELECT * FROM ( SELECT *, ROW_NUMBER() OVER (ORDER BY {}) as rn FROM {}.{} ) x WHERE rn >= {} and rn <= {}".format(
                field_names[0], args.schema, args.table, args.startrow, args.endrow))
        logging.info(
            f'Searching and masking rows {args.startrow}-{args.endrow} of {args.schema}.{args.table}... Output will '
            f'be sent to {args.schema}.{args.target}.')
    else:
        cursor.execute('{} FROM {}.{}'.format(args.query, args.schema, args.table))
        logging.info(f'Searching and masking {args.schema}.{args.table}... Output will be sent to {args.schema}.{args.target}.')
    s = requests.Session()
    url = 'http://localhost:8080/api/darkshield/searchContext.mask'
    urlfile = 'http://localhost:8080/api/darkshield/files/fileSearchContext.mask'
    contextfile = json.dumps({
        "fileSearchContextName": file_search_context_name,
        "fileMaskContextName": file_mask_context_name
    })
    data = cursor.fetchall()
    if args.startrow > 0 and args.endrow > 0:  # remove the additional column that gets returned when selecting from a
        # range of rows.
        data = [row[:-1] for row in data]
    try:
        setup(s)
        data_string = ''
        num_rows = len(data)
        for row_count, row in enumerate(data):
            for col_count, col in enumerate(row):
                if col_count != 0:
                    data_string += args.colsep
                data_string = data_string + str(col)
                if col_count == num_fields - 1 and row_count < num_rows - 1:
                    data_string += args.rowsep
        with s.post(url, json={
            "searchContextName": "SearchContext", "maskContextName": "MaskContext", "text": "{}"
                    .format(data_string)}
                    ) as r:
            if r.status_code >= 300:
                raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
            batchmaskedvalues = [line.split(args.colsep) for line in r.json()['maskedText'].split(args.rowsep)]
        logging.info(f"Sending masked results to target table {args.target}...")
        cursor.executemany("""
                insert into {}.{} {} 
                values ({})""".format(args.schema, args.target, field_names_string, paramstring1), batchmaskedvalues)
        cnxn.commit()
        logging.info("Complete.")
    finally:
        teardown(s)
