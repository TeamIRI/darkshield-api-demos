import json
import logging
import os
from faker import Faker
import random
from random import randint

import requests
import sys
import psycopg2

# Append parent directory to PYTHON_PATH so we can import utils.py
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from requests_toolbelt import MultipartEncoder
from setup import setup, teardown, file_mask_context_name, file_search_context_name
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget

fake = Faker('en_US')

florida_cities = ['Jacksonville', 'Miami', 'Tampa', 'Orlando', 'St. Petersburg', 'Hialeah', 'Port St. Lucie',
                  'Tallahassee', 'Cape Coral', 'Fort Lauderdale', 'Gainesville', 'Lakeland', 'Pensacola', 'Sarasota', 'Fort Myers', 'Melbourne',
                  'Daytona Beach', 'Ocala', 'Panama City', 'Bradenton', 'Naples', 'Punta Gorda', 'Plant City', 'Largo', 'Clearwater',
                  'Hollywood', 'Pembroke Pines', 'West Palm Beach', 'Davie', 'Deltona', 'North Port', 'Tarpon Springs',
                  'Titusville', 'Cocoa Beach', 'Palm Bay', 'Venice', 'Rockledge', 'St. Augustine']

area_codes = ['239', '305', '321', '352', '386', '407', '561', '727', '772', '813', '850', '904', '941', '954']

def sql_execute(command, cur, conn):
    try:
        cur.execute(command)
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as err:
        print(err)
        if conn is not None:
            conn.rollback()


def gen_phone_number():
    phone_number = ''
    phone_number += area_codes[random.randint(0, len(area_codes) - 1)]
    for count in range(9):
        if count == 0 or count == 4:
            phone_number += '-'
        elif count < 4:
            phone_number += str(random.randint(2, 9))
        else:
            phone_number += str(random.randint(0, 9))
    return phone_number

def gen_json():
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = f"{first_name[0].lower()}{last_name.lower()}@ufl.edu"
    address = f"{fake.street_address()}, {florida_cities[random.randint(0, len(florida_cities) - 1)]}, FL"
    return json.dumps({'student_id': randint(10000, 100000), 'info': {'name': f"{first_name} {last_name}", 'score':
        float(random.randrange(5000, 10000)) / 100, 'contact': dict(email=email,
                                                                    address=address,
                                                                    phone=gen_phone_number())}})


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    session = requests.Session()
    try:
        setup(session)
        url = 'http://localhost:8080/api/darkshield/files/fileSearchContext.mask'
        context = json.dumps({
            "fileSearchContextName": file_search_context_name,
            "fileMaskContextName": file_mask_context_name
        })
        f = open("credentials.json", 'r')
        json_creds = json.loads(f.read())
        f.close()
        hostname = json_creds["Hostname"]
        database = json_creds["Database"]
        username = json_creds["Username"]
        password = json_creds["Password"]
        create_sample_table_command = """
            CREATE TABLE sample_json(
                message_id SERIAL PRIMARY KEY,
                message_contents varchar
            )
            """
        create_sample_target_table_command = """
            CREATE TABLE sample_json_masked(
                message_id SERIAL PRIMARY KEY,
                message_contents varchar
            )
            """
        conn = None
        try:
            conn = psycopg2.connect(
                host=hostname,
                database=database,
                user=username,
                password=password)
            cur = conn.cursor()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            if conn is not None:
                conn.rollback()
            else:
                raise Exception("Could not connect to Postgres database.")
        sql_execute("DROP TABLE sample_json", cur, conn)
        sql_execute("DROP TABLE sample_json_masked", cur, conn)
        sql_execute(create_sample_table_command, cur, conn)
        sql_execute(create_sample_target_table_command, cur, conn)
        sql = """INSERT INTO sample_json(message_contents)
                 VALUES(%s);"""
        json_values = []
        for _ in range(random.randint(10, 100)):
            json_value = [gen_json()]
            json_values.append(json_value)
        cur.executemany(sql, json_values)
        conn.commit()
        cur.execute("SELECT message_id, message_contents FROM sample_json")
        batchmaskedvalues = []
        row = cur.fetchone()
        while row is not None:
            rowvalues = []
            encoder = MultipartEncoder(fields={
                'context': ('context', context, 'application/json'),
                'file': ('data.json', row[1], 'application/json')
            })
            with session.post(url, data=encoder, stream=True,
                              headers={'Content-Type': encoder.content_type}) as r:
                if r.status_code >= 300:
                    raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                fileval = ValueTarget()
                parser = StreamingFormDataParser(headers=r.headers)
                parser.register('file', fileval)
                for chunk in r.iter_content(chunk_size=4096):
                    parser.data_received(chunk)
                if len(fileval.value) > 0:
                    rowvalues.append(row[0])
                    rowvalues.append(fileval.value.decode())
                    batchmaskedvalues.append(rowvalues)
            row = cur.fetchone()
        cur.executemany("""
                        INSERT INTO sample_json_masked 
                        VALUES(%s, %s)""",
                        batchmaskedvalues)
        if conn is not None:
            conn.commit()
            conn.close()
    finally:
        teardown(session)
