# DarkShield Files API: Text Search/Masking

This example demonstrates the use of the *darkshield-files* API to search and 
mask text files. To run, the *plankton* web services API must be hosted on 
the location specified in server_config.py (by default *http://localhost:8959*) and must have the *darkshield* and *darkshield-files* 
plugins installed.

The example will search and mask the email and social security number (SSN) 
found inside of text file using regular expression pattern matches. The email
will be hashed while the SSN will have the first 5 digits redacted.

To execute, run *python main.py*.

The results will be placed inside of the *text-masked* directory.
