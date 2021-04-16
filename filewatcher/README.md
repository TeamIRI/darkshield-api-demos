# DarkShield Files API: File Search/Masking thorugh File Watcher

This example demonstrates the use of the *darkshield-files* API to search and 
mask text files. To run, the *plankton* web services API must be hosted on 
*http://localhost:8080* and must have the *darkshield* and *darkshield-files* 
plugins installed.

The example will search and mask the email and social security number (SSN) 
found inside of text file using regular expression pattern matches. The email
will be hashed while the SSN will have the first 5 digits redacted.

To execute, run *python main.py*, or *pythonw main.py* to run in the background.

The results will be placed inside of the *masked* directory.

The watcher will watch for any modified or newly created files in a certain directory (recursively, or non-recursively).
The file will be sent to the DarkShield Files API, and, if it is a supported file type, will be masked based on the matchers and masking
rules provided. Those matchers are only for emails and social security numbers in this demo. The watcher will run indefinitely until
either the process is stopped, or, if running from the command line, ctrl-c is pressed.
