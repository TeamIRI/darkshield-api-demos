# DarkShield Files API: Text Search/Masking

## Synopsis

This example demonstrates the use of the *darkshield-files* API to search and 
mask a text file.

## Requirements

The *plankton* web services API must be hosted at
the location specified in *server_config.py* (by default *http://localhost:8959*) with the *darkshield* and *darkshield-files* 
plugins installed. 

Python 3 and all of the dependencies specified in the *requirements.txt* file located at the root of this repository must be installed.

## Search Matchers and Masking Rules

The specifications of what type of data to search for, and how to mask each type of data, are specified programatically in the *setup.py* Python source code file.

The *setup.py* file can be freely modified to fine-tune search matchers and paired masking rules to specific requirements.

This example will search for and mask the email and Social Security Number (SSN) 
found inside of the text file using regular expression pattern matches.

The email will be hashed while the SSN will have the first 5 digits redacted.

## Running the Demo

To execute, run `python main.py`.

The results will be placed inside of the *text-masked* directory.
