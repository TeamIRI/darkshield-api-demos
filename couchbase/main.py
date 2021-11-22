import json
import os
import logging
import requests
import sys
import argparse
from couchbase.cluster import Cluster, ClusterOptions
from couchbase_core.cluster import PasswordAuthenticator
from couchbase.cluster import QueryOptions
import ast
import time

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from requests_toolbelt import MultipartEncoder
from setup import setup, teardown, file_mask_context_name, file_search_context_name
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget, FileTarget, NullTarget
from utils import base_url

f = open("credentials.json", 'r')
json_creds = json.loads(f.read())
f.close()
user = json_creds["User"]
password = json_creds["Password"]
mask_bucket = json_creds["MaskBucket"]
mask_scope = json_creds["MaskScope"]
mask_coll = json_creds["MaskCollection"]
cluster = Cluster('couchbase://localhost', ClusterOptions(PasswordAuthenticator(user, password)))

employees = [{
  "_id": "123",
  "company": "Microsoft",
  "name": "Kathy Wynn",
  "gender": "female",
  "email": "kathy@duoflex.com",
  "phone": "+1 (843) 400-3871"
}, 
{
  "_id": "124",
  "company": "Amazon",
  "name": "Adam Smith",
  "gender": "male",
  "email": "adam@tothestars.com",
  "phone": "+1 (567) 348-3167"
},
{
  "_id": "128",
  "company": "Google",
  "name": "Robert Hathaway",
  "gender": "male",
  "email": "robert@overtheclouds.com",
  "phone": "+1 (843) 490-9999"
}]



def lookup_by_callsign(cs, collection):
  print("\nLookup Result: ")
  try:
    sql_query = 'SELECT * FROM '+collection
    row_iter = cluster.query(
      sql_query,
      QueryOptions(positional_parameters=[cs]))
    for row in row_iter: print(row)
  except Exception as e:
    print(e)

def upsert_document(key, doc): 
  try:
    cb_coll.upsert(key, doc)
  except Exception as e:
    print(e)


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    session = requests.Session()
    parser = argparse.ArgumentParser(description='Demo for Couchbase collection search/masking.')
    parser.add_argument('bucket_name', type=str, help="The bucket to query.")
    parser.add_argument('scope_name', type=str, help="The scope in bucket.")
    parser.add_argument('collection_name', type=str, help="The collection in the scope.")
    args = parser.parse_args()
    bucket = args.bucket_name
    scope = args.scope_name
    collection =args.collection_name
    bucket_scope_collection = bucket+'.'+scope+'.'+collection
    cb = cluster.bucket(bucket)
    cb_coll = cb.scope(scope).collection(collection)
    maskcb_coll = cb.scope(scope).collection(mask_coll)
    maskedbucket_scope_collection = mask_bucket+'.'+mask_scope+'.'+mask_coll
    for employee in employees:
        key = employee['company']+ '_' + employee['_id']
        upsert_document(key, employee)
    try:
        setup(session)
        url = f'{base_url}/files/fileSearchContext.mask'
        context = json.dumps({
            "fileSearchContextName": file_search_context_name,
            "fileMaskContextName": file_mask_context_name
        })

        try:
            sql_query = 'SELECT * FROM ' + bucket_scope_collection
            row_iter = cluster.query(
                sql_query,
                QueryOptions(positional_parameters=["CBS"]))
            i=1
            
            for row in row_iter:
                key = row[collection]['company']+ '_' + row[collection]['_id']
                row_result = list(row.values())
                str_value = json.dumps(row_result, indent=True)
                name = "item"+str(i)+".json"
                process_files = [(name, 'application/json')]
                for file_name, media_type in process_files:
                    f = str_value
                    encoder = MultipartEncoder(fields={
                        'context': ('context', context, 'application/json'),
                        'file': (file_name, f, media_type)
                    })
                logging.info(f"POST: sending '{file_name}' to {url}")
                with session.post(url, data=encoder, stream=True,
                                    headers={'Content-Type': encoder.content_type}) as r:
                    if r.status_code >= 300:
                        raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                    parser = StreamingFormDataParser(headers=r.headers)
                    i=i+1
                    my_bytes_value = ValueTarget()
                    parser.register('file', my_bytes_value) 
                    for chunk in r.iter_content(4096):
                        parser.data_received(chunk)     
                    bson_value = my_bytes_value.value
                    data = bson_value.decode('utf-8')
                    dictionary = ast.literal_eval(data)
                    for d in dictionary:
                        try:
                            maskcb_coll.upsert(key, d)
                        except Exception as e:
                            print(e)


        except Exception as e:
            print(e)

    finally:
            teardown(session)
print("Printing results...")
time.sleep(1)
lookup_by_callsign("CBS", maskedbucket_scope_collection)

