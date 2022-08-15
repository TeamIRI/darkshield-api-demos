# DarkShield Files API: HL7 v2 Message Search/Masking

This example demonstrates the use of the *darkshield-files* API to search and 
mask text files. To run, the *plankton* web services API must be hosted on 
the location specified in server_config.py (by default *http://localhost:8959*) and must have the *darkshield* and *darkshield-files* 
plugins installed.

The example will find and mask the following:
Names (NamesMatcher): Use the Named Entity Recognition (NER) matcher to search through the fields.
Columns (ColumnMatcher): Use a column matcher with the segment ID and column specified (e.g. PID|3) to search through HL7 message.
Emails (EmailMatcher): Use a regular expression matcher to search through the fields for emails.

The masking rule applied to PII in this example will be using Format Preserving encryption.

To use the NER matcher user must install NER model once after initial download of DarkShield API.
To install NER model traverse through Plankton root directory to ./utils and execute python model_util.py
to begin download of English pytorch NER model.

To execute DarkShield demo, run *python main.py*.

The results will be placed inside of the *hl7-masked* directory.
