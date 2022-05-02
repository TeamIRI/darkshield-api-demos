# DarkShield Files API: Fixed Width File Search/Masking

## Overview

This example demonstrates the use of the *darkshield-files* API to search and 
mask fixed width files. 

## Requirements 
To run, the *plankton* web services API must be hosted on 
the location specified in *server_config.py* (by default *http://localhost:8959*) with both the *darkshield* and *darkshield-files* 
plugins installed.

This demo requires version 1.3.0 or greater of the DarkShield API.

The content type **must** be passed as *'text/fixed'* in the request to the DarkShield API in order for the file to be processed as a fixed width file rather than an unstructured text file.

A configuration option specifying the column widths of the fixed width file must also
be passed in as an option to the FileSearchContext.

## Search Matchers and Masking Rules

The example will search and mask the email and Social Security Number (SSN) 
found inside of a fixed-width text file using regular expression pattern matches.

The email
will be encrypted with format-preserving encryption while the SSN will have the 
first 5 digits redacted.

## Execution of the Demo

To execute, run `python main.py`.

The results will be placed inside of the *fixed-width-masked* directory.
