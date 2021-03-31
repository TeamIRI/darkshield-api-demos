import io
import json
import logging
import base64
import os
import mysql.connector
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
    if len(sys.argv) < 6:
        print("Usage: python main.py [host] [username] [password] [database] [table]")
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
        database=sys.argv[4]
        mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
      )
        mycursor = mydb.cursor()
        table=sys.argv[5]
        # get all the data from specified table
        mycursor.execute("SELECT * FROM {}".format(table))
        logging.info("Getting data from database '{}' table '{}'.".format(database,table))
        myresult = mycursor.fetchall()
        s=requests.Session()
        count=0
        field_names = [i[0] for i in mycursor.description]
        data_types = [i[1] for i in mycursor.description]
        # loop through rows, then values
        for row in myresult:
            # log progess every 25 rows
            if count % 25 == 0:
                logging.info("Masking row {} of table '{}'.".format(count+1,table))
            firstval=''
            firstNum=0
            colNum=0
            for value in row:
                # if this is a blob type, handle differently
                # this covers tinyblob to longblob data types;
                if data_types[colNum] >= 249 and data_types[colNum] <= 252:
                    try:
                        files = {'file': io.BytesIO(value), 'context': contextfile}
                        with s.post(urlfile, files=files, stream=True) as r:
                            if r.status_code >= 300:
                                raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                            fileval=ValueTarget()
                            parser = StreamingFormDataParser(headers=r.headers)
                            parser.register('file', fileval)
                            #parser.register('results', FileTarget(f'resultsblob.json'))
                            for chunk in r.iter_content():
                                parser.data_received(chunk)
                            query = "UPDATE {} SET {} = %s WHERE {} = %s".format(table,field_names[colNum],field_names[firstNum])
                            if len(fileval.value) > 0:
                                args = (fileval.value,firstval)
                                try:
                                    mycursor.execute(query,args)
                                except Exception as e:
                                    print('error: ')
                                    print(e)
                                    pass
                                mydb.commit()
                    except Exception as e:
                        print('error: ')
                        print(e)
                        pass
                else:
                # try to get a value to use as a reference for update statements. Hopefully a unique row id.
                    if firstval == '':
                        firstval = value
                        firstnum =colNum
                    # unstructured text or basic values; handle using base DarkShield API
                    
                    with s.post(url, json={"searchContextName": "SearchContext","maskContextName": "MaskContext","text": "{}".format(value)}) as r:
                        if r.status_code >= 300:
                            raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                        query = "UPDATE {} SET {} = %s WHERE {} = %s".format(table,field_names[colNum],field_names[firstNum])
                        args=(r.json()['maskedText'], firstval)
                        try:
                            mycursor.execute(query,args)
                        except Exception as e:
                            print('error: ')
                            print(e)
                            pass
                        mydb.commit()
                colNum+=1
            count+=1
             # uncomment to end after certain number of rows
            #if count>=1:
                #exit(0)
        logging.info("Completed masking {} rows of table '{}'.".format(count,table))        
    finally:
        teardown()