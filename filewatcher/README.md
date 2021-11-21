# DarkShield Files API: File Search/Masking thorugh File Watcher

This example demonstrates the use of the *darkshield-files* API to search and 
mask text files. To run, the *plankton* web services API must be hosted on 
the location specified in server_config.py (by default *http://localhost:8959*) and must have the *darkshield* and *darkshield-files* 
plugins installed.

The example will search and mask the email and social security number (SSN) 
found inside of text file using regular expression pattern matches. The email
will be hashed while the SSN will have the first 5 digits redacted.

To install the additional dependencies, execute *pip install -r requirements.txt* 
(make sure your virtual environment is activated, or your dependencies will 
be installed globally).

To execute, run *python main.py directory*, or *pythonw main.py directory* to run in the background. Other options include -h for help, 
and -r to search the directory specified recursively. 

The full usage details are as follows:

usage: main.py [-h] [-r] directory

File watcher for newly modified and created file search/masking.

positional arguments:
  directory        The directory to use for the search. If it doesn't exist, it will be created.

optional arguments:
  -h, --help       show this help message and exit
  -r, --recursive  Search directory recursively.


The results will be placed inside of the *masked* directory.

The watcher will watch for any modified or newly created files in a certain directory (recursively, or non-recursively). The 
file will be sent to the DarkShield Files API, and, if it is a supported file type, will be masked based on the matchers and masking
rules provided. 

Those matchers are only for emails and Social Security numbers in this demo. The matchers and masking rules may be modified 
by editing setup.py. 

The watcher will run indefinitely until either the process is stopped, or, if running 
from the command line, ctrl-c is pressed.
