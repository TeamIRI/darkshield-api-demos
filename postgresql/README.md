# DarkShield Files API: Search/Masking JSON in PostgreSQL

This example demonstrates the use of the *darkshield-files* API to search and mask JSON data in a PostgreSQL database. 
To run, the *plankton* web services API must be hosted on 
*http://localhost:8959* and must have the *darkshield* and *darkshield-files* plugins installed. 

Additionally, an accessible instance of PostgreSQL must be running. Credentials to access PostgreSQL can be configured in the *credentials.json* file. 
Hostname of the PostgreSQL server, database name, username, and password should be specified in that file.

The demo will create two database tables - *sample_json* and *sample_json_masked* with a column containing the primary key and
a column containing randomly-generated JSON data. Between 10 and 100 rows will be generated, inclusive. The data is generated in
the *sample_json* table. The *sample_json* table is read from, with each value in the column containing JSON sent to the
*darkshield-files* API for search and masking. The masked results are output to the *sample_json_masked* table.

The example will find and mask the following:

1. Emails (EmailMatcher): Found using a regular expression and masked using a hashing
function.
2. Phone Numbers (PhoneMatcher): Found using a regular expression and masked using
format-preserving encryption.
3. Names (NameMatcher): Found using a Named Entity Recognition (NER) model AND using
JSON paths (all names can be found in the 'name' key/tag, regardless
of nesting).
4. Addresses (AddressMatcher): Found using a JSON path. Matches all JSON values with an 'address' key name.
Masked using format-preserving encryption.

To execute, run *python main.py*.

The contents of the masked table may be viewed through the Data Source Explorer in IRI Workbench to confirm the results.

The setup script will also download the NER and sentence detection models from the
[OpenNLP website](http://opennlp.sourceforge.net/models-1.5/) if not present in the
directory. If you are having trouble downloading the models, place the *en-ner-person.bin*
and *en-sent.bin* files into this directory.
