import io
import json
import logging
import os
import cx_Oracle
import requests
import sys

# Append parent directory to PYTHON_PATH so we can import utils.py
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from setup import setup, teardown, file_mask_context_name, file_search_context_name
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget

# Demo2: Mask data from an Oracle table and send to a different output table.
if __name__ == "__main__":
    if len(sys.argv) < 8:
        print("Usage: python {} [host] [username] [password] [service_name] [database] [table] [output_table]".format(
            sys.argv[0]))
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
        service_name = sys.argv[4]
        connection = cx_Oracle.connect(user, password, "{}/{}".format(host, service_name))
        cursor = connection.cursor()
        database = sys.argv[5]
        table = sys.argv[6]
        output_table = sys.argv[7]
        # get all the data from specified table
        cursor.execute("SELECT * FROM {}".format(table))
        result = cursor.fetchall()
        logging.info("Getting data from database '{}' table '{}'.".format(database, table))
        count = 0
        field_names = [i[0] for i in cursor.description]
        data_types = [i[1] for i in cursor.description]
        num_fields = len(field_names)
        field_names_string = "("
        paramstring1 = ""
        paramstring2 = ":"+str(num_fields+1)
        for w in range(num_fields):
            if w == num_fields - 1:
                field_names_string = field_names_string+field_names[w]+")"
                paramstring1 = paramstring1+":"+str(w+1)
                break
            field_names_string = field_names_string+field_names[w]+", "
            paramstring1 = paramstring1+":"+str(w+1)+", "
        batchvalues = []
        batchmaskedvalues = []
        keyvalues = []
        pkeyvalues = []
        # loop through rows, then values

        for row in result:
            keyvalues.append(count)
            rowvalues = []
            rowmaskedvalues = []
            # log progess every 25 rows
            if count % 25 == 0:
                logging.info("Masking row {} of table '{}'.".format(count+1, table))
            firstval = ''
            firstNum = 0
            colNum = 0
            for value in row:
                # if this is a blob type, handle differently
                if data_types[colNum] == cx_Oracle.DB_TYPE_BLOB:
                    value2 = value.read()
                    rowvalues.append(value2)
                    files = {'file': io.BytesIO(value2), 'context': contextfile}
                    with s.post(urlfile, files=files, stream=True) as r:
                        if r.status_code >= 300:
                            raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                        fileval = ValueTarget()
                        parser = StreamingFormDataParser(headers=r.headers)
                        parser.register('file', fileval)
                        # parser.register('results', FileTarget("resultsblob{}_{}.json".format(count,colNum)))
                        for chunk in r.iter_content(chunk_size=4096):
                            parser.data_received(chunk)
                        query = "UPDATE {} SET {} = :1 WHERE {} = :2".format(table, field_names[colNum],
                                                                             field_names[firstNum])
                        if len(fileval.value) > 0:
                            rowmaskedvalues.append(fileval.value)
                        else:
                            rowmaskedvalues.append(value)
                else:
                    rowvalues.append(value)
                # try to get a value to use as a reference for update statements. Hopefully a unique row id.
                    if firstval == '':
                        firstval = value
                        firstnum = colNum
                        pkeyvalues.append(firstval)
                    # unstructured text or basic values; handle using base DarkShield API
                    with s.post(url, json={
                        "searchContextName": "SearchContext", "maskContextName": "MaskContext", "text": "{}"
                                .format(value)}
                                ) as r:
                        if r.status_code >= 300:
                            raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
                        rowmaskedvalues.append(r.json()['maskedText'])
                colNum += 1
                if colNum == num_fields:
                    batchvalues.append(rowvalues)
                    batchmaskedvalues.append(rowmaskedvalues)
            count += 1
            if count % 2000 == 0:
                cursor.executemany("""
        insert into {} {} 
        values ({})""".format(output_table, field_names_string, paramstring1), batchmaskedvalues)
                connection.commit()
                batchvalues = []
                batchmaskedvalues = []
                keyvalues = []
                pkeyvalues = []
                # uncomment to end after certain number of rows
                # if count>=rows:
                #   return 1
        logging.info("Sending final batch.")
        countt = 0
        cursor.executemany("""
        insert into {} {} 
        values ({})""".format(output_table, field_names_string, paramstring1), batchmaskedvalues)
        connection.commit()
        logging.info("Completed masking {} rows of table '{}'.".format(count, table))
    finally:
        teardown(s)
