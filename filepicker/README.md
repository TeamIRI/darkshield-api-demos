# DarkShield Files API: File Search/Masking through Interactive File Picker

This example demonstrates the use of the *darkshield-files* API to search and 
mask files picked through a file browser. To run, the *plankton* web services API must be hosted on 
*http://localhost:8080* and must have the *darkshield* and *darkshield-files* 
plugins installed.

The example will search and mask the email and social security number (SSN) 
found inside of text file using regular expression pattern matches. The email
will be hashed while the SSN will have the first 5 digits redacted.

To install the additional dependencies, execute *pip install -r requirements.txt* 
(make sure your virtual environment is activated, or your dependencies will 
be installed globally).

To execute, run *python main.py*.

The results will be placed inside of the *masked* directory.

The example will continue to run so long as a file is picked.
