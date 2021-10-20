import json
import logging
import os
import cassandra
import requests
import sys
import uuid
from cassandra.cluster import Cluster
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.management import sync_table

# Append parent directory to PYTHON_PATH so we can import utils.py
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from setup import setup, teardown
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget, FileTarget

# This demo will setup Search and Mask Contexts for the DarkShield API, connect to Cassandra
# at the default localhost, port 9042, create a 'test' keyspace if it does not already exist,
# create a 'person' table with an id, first name, last name, and blob,
# insert values into the table, read the newly inserted values, send to the DarkShield API,
# and update the values with the masked response.


class Person(Model):
    id = columns.UUID(primary_key=True)
    first_name = columns.Text()
    last_name = columns.Text()
    blob = columns.Blob()


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    session = requests.Session()
    url_file = 'http://localhost:8080/api/darkshield/files/fileSearchContext.mask'
    url_base = 'http://localhost:8080/api/darkshield/searchContext.mask'
    context = json.dumps({
        "fileSearchContextName": "FileSearchContext",
        "fileMaskContextName": "FileMaskContext"
    })
    try:
        setup(session)
        with open('blob.pdf', 'rb') as f:
            data = f.read()
        cluster = Cluster()
        cassandra_session = cluster.connect()
        try:
            cassandra_session.execute(
                "CREATE KEYSPACE test WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };")
        except cassandra.AlreadyExists:  # ignore if the keyspace has already been created.
            pass
        cassandra_session.set_keyspace('test')
        sync_table(Person, ['test'], connections=(cassandra.cqlengine.connection.default(),))
        cassandra_session.execute(
            """
            TRUNCATE TABLE test.person
            """)
        uid = uuid.uuid1()
        cassandra_session.execute(
            """
            INSERT INTO person (id, first_name, last_name, blob)
            VALUES (%s, %s, %s, %s)
            """,
            (uid, "John", "Doe", data))
        rows = cassandra_session.execute("SELECT id, first_name, last_name, blob FROM person")
        for row in rows:
            with session.post(url_base, json={"searchContextName": "SearchContext", "maskContextName": "MaskContext",
                                              "text": "{}".format(row[1])}) as r:
                if r.status_code >= 300:
                    raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                logging.info('Putting masked response text \'{}\' into table...'.format(r.json()['maskedText']))
                cassandra_session.execute(
                    "UPDATE person SET first_name='{}' WHERE id ={}".format(r.json()['maskedText'], row[0]))
            with session.post(url_base, json={"searchContextName": "SearchContext", "maskContextName": "MaskContext",
                                              "text": "{}".format(row[2])}) as r:
                if r.status_code >= 300:
                    raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                logging.info('Putting masked response text \'{}\' into table...'.format(r.json()['maskedText']))
                cassandra_session.execute(
                    "UPDATE person SET last_name='{}' WHERE id ={}".format(r.json()['maskedText'], row[0]))
            files = {'file': data, 'context': context}
            with session.post(url_file, files=files, stream=True) as r:
                if r.status_code >= 300:
                    raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                os.makedirs('masked', exist_ok=True)
                with open('masked/original.pdf', 'wb') as f:
                    f.write(row[3])
                fileval = ValueTarget()
                parser = StreamingFormDataParser(headers=r.headers)
                parser.register('file', fileval)
                parser.register('file', FileTarget(f'masked/blob_masked.pdf'))
                parser.register('results', FileTarget(f'masked/blob_results.json'))
                for chunk in r.iter_content():
                    parser.data_received(chunk)
                logging.info('Putting masked response blob into table...')
                query = "UPDATE person SET blob=? WHERE id=?"
                prepared = cassandra_session.prepare(query)
                cassandra_session.execute(prepared, (fileval.value, row[0]))
        cluster.shutdown()
    finally:
        teardown(session)
