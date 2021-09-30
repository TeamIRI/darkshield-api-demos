# DarkShield Files API: Fixed Width File Search/Masking

This example demonstrates the use of the *darkshield-files* API to search and 
mask fixed width files. To run, the *plankton* web services API must be hosted on 
*http://localhost:8080* and must have the *darkshield* and *darkshield-files* 
plugins installed.

This demo requires version 1.3.0 or greater of the DarkShield API.
The content type must be passed as 'text/fixed' for the file to be processed as a fixed width file rather than an unstructured text file.
A configuration option specifying the column widths of the fixed width file must 
be passed in as an option to the FileSearchContext.

The example will search and mask the email and social security number (SSN) 
found inside of text file using regular expression pattern matches. The email
will be encrypted with format preserved encryption while the SSN will have the 
first 5 digits redacted.

To execute, run *python main.py*.

The results will be placed inside of the *fixed-width-masked* directory.
