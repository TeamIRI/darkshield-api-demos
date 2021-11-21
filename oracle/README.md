# DarkShield Files API: Oracle Search/Masking

This example demonstrates the use of the *darkshield-files* API to search and mask Oracle database values. To run, the *plankton* web services API must be hosted on 
the location specified in server_config.py (by default *http://localhost:8959*) and must have the *darkshield* and *darkshield-files* plugins 
installed.

You must have an Oracle database installed and hosted on *http://localhost:1521*. The Oracle client libraries must be 
installed as well. Python 3 should be used.

To install the additional dependencies, execute *pip install -r requirements.txt* 
(make sure your virtual environment is activated, or your dependencies will 
be installed globally).

The script will search all values in the database and table specified, and mask based on predefined rules.

The example will find and mask the following:

1. Social Security Numbers (SsnMatcher): Found using a regular expression. The first 5 digits of the Social Security Number,
excluding the dashes, will be redacted with the '*' character.
2. Names (NameMatcher): Found using a Named Entity Recognition (NER) model. Will encrypt the names with 
format-preserving alphanumeric encryption.

To execute the first demo script, run *python demo1.py [host] [username] [password] [service_name] [database] [table]*.
The first demo script will mask data from the table in place.
To execute the second demo script, run *python demo2.py [host] [username] [password] [service_name] [database] [table] [output table]*. 
The second demo script will send masked data to another table, which must already exist and be set up with the same columns and data types.


The setup script will also download the NER and sentence detection models from the
[OpenNLP website](http://opennlp.sourceforge.net/models-1.5/) if not present in the
directory. If you are having trouble downloading the models, place the *en-ner-person.bin*
and *en-sent.bin* files into this directory.