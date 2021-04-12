import io
import json
import logging
import base64
import os
import cx_Oracle
import re
import requests
import sys

# Append parent directory to PYTHON_PATH so we can import utils.py
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from setup import setup, teardown, file_mask_context_name, file_search_context_name
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget, FileTarget,NullTarget

if __name__ == "__main__":
# args: [host] [username] [password] [database] [table]
        if len(sys.argv) < 7:
            print("Usage: python main.py [host] [username] [password] [dsn] [database] [table]")
            print("Please provide all arguments.")
            exit(0)
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
        url = 'http://localhost:8080/api/darkshield/searchContext.mask'
        urlfile = 'http://localhost:8080/api/darkshield/files/fileSearchContext.mask'
        contextfile = json.dumps({
                "fileSearchContextName": file_search_context_name,
                "fileMaskContextName": file_mask_context_name
            })
        try:
            setup()
            host=sys.argv[1]
            user=sys.argv[2]
            password=sys.argv[3]
            dsn=sys.argv[4]
            connection =cx_Oracle.connect(
           user=user,
           password=password,
           dsn=dsn
           )
           
            cursor=connection.cursor()
            database = sys.argv[5]
            table = sys.argv[6]
            # get all the data from specified table
            cursor.execute("SELECT * FROM {}".format(table))
            result=cursor.fetchall()
            logging.info("Getting data from database '{}' table '{}'.".format(database,table))
            s=requests.Session()
            count=0
            field_names = [i[0] for i in cursor.description]
            data_types = [i[1] for i in cursor.description]
            # loop through rows, then values
            for row in result:
                # log progess every 25 rows
                if count % 25 == 0:
                    logging.info("Masking row {} of table '{}'.".format(count+1,table))
                firstval=''
                firstNum=0
                colNum=0
                for value in row:
                    # if this is a blob type, handle differently
                    if data_types[colNum] == cx_Oracle.DB_TYPE_BLOB:
                        value2=value.read()
                        files = {'file': io.BytesIO(value2), 'context': contextfile}
                        with s.post(urlfile, files=files, stream=True) as r:
                            if r.status_code >= 300:
                                raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                            fileval=ValueTarget()
                            parser = StreamingFormDataParser(headers=r.headers)
                            parser.register('file', fileval)
                            #parser.register('results', FileTarget("resultsblob{}_{}.json".format(count,colNum)))
                            for chunk in r.iter_content():
                                parser.data_received(chunk)
                            query = "UPDATE {} SET {} = :1 WHERE {} = :2".format(table,field_names[colNum],field_names[firstNum])
                            if len(fileval.value) > 0:
                                args = (fileval.value,firstval)
                                cursor.execute(query,args)
                                connection.commit()
                    else:
                    # try to get a value to use as a reference for update statements. Hopefully a unique row id.
                        if firstval == '':
                            firstval = value
                            firstnum =colNum
                        # unstructured text or basic values; handle using base DarkShield API
                        with s.post(url, json={"searchContextName": "SearchContext","maskContextName": "MaskContext","text": "{}".format(value)}) as r:
                            if r.status_code >= 300:
                                raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                            query = "UPDATE {} SET {} = :1 WHERE {} = :2".format(table,field_names[colNum],field_names[firstNum])
                            args=(r.json()['maskedText'], firstval)
                            cursor.execute(query,args)
                            connection.commit()
                    colNum+=1
                count+=1
                 # uncomment to end after certain number of rows
                #if count>=rows:
                 #   return 1
            logging.info("Completed masking {} rows of table '{}'.".format(count,table))
        finally:
            teardown()