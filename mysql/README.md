# DarkShield Files API: MySQL Search/Masking

This example demonstrates the use of the *darkshield-files* API to search and mask MySQL database values. To run, the *plankton* web services API must be hosted on 
*http://localhost:8959* and must have the *darkshield* and *darkshield-files* plugins 
installed.

You must have a MySQL database installed and hosted on *http://localhost:3306*. The Python MySQL connector must be 
installed as well. Python 3 should be used.

The new_table.sql file will create a sample table named 'new_table' with two rows of personal data. This includes a blob column that has an image in the first row, and a PDF in the second row.

To install the additional dependencies, execute *pip install -r requirements.txt* 
(make sure your virtual environment is activated, or your dependencies will 
be installed globally).

The script will search all values in the database and table specified, and mask based on predefined rules.

The example will find and mask the following:

1. Social Security Numbers (SsnMatcher): Found using a regular expression. The first 5 digits of the Social Security Number,
excluding the dashes, will be redacted with the '*' character.
2. Names (NameMatcher): Found using a Named Entity Recognition (NER) model. Will encrypt the names with 
format-preserving alphanumeric encryption.

To execute, run *python main.py [host] [username] [password] [database] [table]*.


The setup script will also download the NER and sentence detection models from the
[OpenNLP website](http://opennlp.sourceforge.net/models-1.5/) if not present in the
directory. If you are having trouble downloading the models, place the *en-ner-person.bin*
and *en-sent.bin* files into this directory.