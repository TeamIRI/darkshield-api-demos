# DarkShield Files API: SQL Server Search/Masking

This example demonstrates the use of the *darkshield* and *darkshield-files* API to search and mask SQL Server database values. To run, the *plankton* web services API must be hosted on 
*http://localhost:8080* and must have the *darkshield* and *darkshield-files* plugins 
installed.

You must have a SQL Server database installed and hosted. The *pyodbc* Python module must be 
installed as well. Python 3 should be used.

To install the additional dependencies, execute *pip install -r requirements.txt* 
(make sure your virtual environment is activated, or your dependencies will 
be installed globally).

There are two demos present in this folder.

The first demo (sql_server_all.py) should be run if there are blob columns to mask.

The usage is as follows:

sql_server_all.py [-h] [-H HOSTNAME] [-P PORT] -u USERNAME -p PASSWORD -d DATABASE -t TABLE -T TARGET -s SCHEMA [-q QUERY] [-b BATCHSIZE]

The hostname and port arguments are optional, and default to *localhost* and *1433*, respectively. A username, password, database name, table name, target table name, and schema should be specified.

Additionally, a query can be specified to select certain columns and/or rows. The default query used is SELECT *. The batchsize specifies after how many rows to insert the masked results into the target table and clear the data values held in memory.

The second demo (sql_server_text.py) can handle textual columns more rapidly, but the columns must not contain any blobs. A column separator and row separator must also be specified that is not present in any of the values.
The usage is:

sql_server_text.py [-h] [-H HOSTNAME] [-P PORT] -u USERNAME -p PASSWORD -d DATABASE -t TABLE -T TARGET -s SCHEMA [-q QUERY] [-a ROWSEP] [-b COLSEP] [-S STARTROW] [-E ENDROW]

The example will find and mask the following:

1. Social Security Numbers (SsnMatcher): Found using a regular expression. The first 5 digits of the Social Security Number,
excluding the dashes, will be redacted with the '*' character.
2. Names (NameMatcher): Found using a Named Entity Recognition (NER) model. Will encrypt the names with 
format-preserving alphanumeric encryption.

The setup script will also download the NER and sentence detection models from the
[OpenNLP website](http://opennlp.sourceforge.net/models-1.5/) if not present in the
directory. If you are having trouble downloading the models, place the *en-ner-person.bin*
and *en-sent.bin* files into this directory.
