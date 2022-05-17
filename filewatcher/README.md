# Searching/Masking Newly Added or Modified Files in a Directory

## Synopsis

This example watches a directory for changes to existing files or the addition of any new files to the directory. 

If a file has been modified or newly added, it is sent to the DarkShield API for searching and masking. 

The masked file and JSON-formatted masking results received as a response from the DarkShield API are placed in the *masked* directory.

## Requirements
To run, the DarkShield API must be hosted at 
the location specified in *server_config.py* (by default *http://localhost:8959*) with both the *darkshield* and *darkshield-files* 
plugins installed.

To install the additional dependencies, execute *pip install -r requirements.txt* 
(make sure your virtual environment is activated, or your dependencies will 
be installed globally).

## Search Matchers and Rules

DarkShield uses search matchers to find data, and pairs matchers with rules to transform the matched data consistently.

In this example, search and mask contexts are set up programatically at the start of the program and automatically cleaned up when the program terminates.

The definitions for search and mask contexts are contained in the *setup.py* source file. The matchers and masking rules may be modified 
by editing setup.py. 

This example will search and mask emails and Social Security numbers (SSNs) 
found using regular expression pattern matches. 

Emails will be hashed while the SSNs will have the first 5 digits redacted.

## Execution

To execute, run `python main.py directory`, or `pythonw main.py directory` to run in the background. Other options include `-h` for help, 
and `-r` to search the directory specified recursively. 

The full usage details are as follows:

usage: `main.py [-h] [-r] directory`

> ### Positional Arguments:
> **directory** -
> The directory to use for the search. If it doesn't exist, it will be created.
>
> ### Optional Arguments:
> -h, --*help* -    Show help message and exit
> 
> -r, --*recursive* - Search directory recursively.

## Additional Details

The watcher will watch for any modified or newly created files in a certain directory (recursively, or non-recursively). 

The file will be sent to the DarkShield API, and, if it is a supported file type, will be masked based on the matchers and masking
rules provided. 

The watcher will run indefinitely until either the process is stopped, or, if running 
from the command line, `ctrl-c` is pressed.

