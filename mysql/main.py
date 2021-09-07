import io
import json
import logging
import os
import mysql.connector
import requests
import sys

# Append parent directory to PYTHON_PATH so we can import utils.py
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from setup import setup, teardown, file_mask_context_name, file_search_context_name
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget

if __name__ == "__main__":
    # args: [host] [username] [password] [database] [table]
    if len(sys.argv) < 6:
        print("Usage: python main.py [host] [username] [password] [database] [table]")
        print("Please provide all arguments.")
        exit(0)
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
        host = sys.argv[1]
        user = sys.argv[2]
        password = sys.argv[3]
        database = sys.argv[4]
        mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        mycursor = mydb.cursor()
        table = sys.argv[5]
        # get all the data from specified table
        mycursor.execute("SELECT * FROM {}".format(table))
        logging.info("Getting data from database '{}' table '{}'.".format(database, table))
        myresult = mycursor.fetchall()
        count = 0
        field_names = [i[0] for i in mycursor.description]
        data_types = [i[1] for i in mycursor.description]
        # loop through rows, then values
        for row in myresult:
            # log progess every 25 rows
            if count % 25 == 0:
                logging.info("Masking row {} of table '{}'.".format(count+1, table))
            firstval = ''
            firstNum = 0
            colNum = 0
            for value in row:
                # if this is a blob type, handle differently
                # this covers tinyblob to longblob data types;
                # ensure this is a file and not floating text.
                if type(value) == bytes:
                    if 249 <= data_types[colNum] <= 252:
                        files = {'file': io.BytesIO(value), 'context': contextfile}
                        with s.post(urlfile, files=files, stream=True) as r:
                            if r.status_code >= 300:
                                raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                            fileval = ValueTarget()
                            parser = StreamingFormDataParser(headers=r.headers)
                            parser.register('file', fileval)
                            for chunk in r.iter_content():
                                parser.data_received(chunk)
                            query = "UPDATE {} SET {} = %s WHERE {} = %s".format(table, field_names[colNum],
                                                                                 field_names[firstNum])
                            if len(fileval.value) > 0:
                                args = (fileval.value, firstval)
                                mycursor.execute(query, args)
                                mydb.commit()
                else:
                    # try to get a value to use as a reference for update statements. Hopefully a unique row id.
                    if firstval == '':
                        firstval = value
                        firstnum = colNum
                    # unstructured text or basic values; handle using base DarkShield API
                    with s.post(url, json={"searchContextName": "SearchContext", "maskContextName":
                                "MaskContext", "text": "{}".format(value)}) as r:
                        if r.status_code >= 300:
                            raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                        query = "UPDATE {} SET {} = %s WHERE {} = %s".format(table, field_names[colNum],
                                                                             field_names[firstNum])
                        args = (r.json()['maskedText'], firstval)
                        mycursor.execute(query, args)
                        mydb.commit()
                colNum += 1
            count += 1
            # uncomment to end after certain number of rows
            # if count>=rows:
            #   return 1
        logging.info("Completed masking {} rows of table '{}'.".format(count, table))
    finally:
        teardown(s)
