# DarkShield API: Pseudonymization and Restore

## Synopsis

This demo demonstrates consistently pseudonymizing names to other names, and restoring names to their original value.

## Requirements

To set up, a two-column, tab-separated file containing a list of names mapped to other names should be produced. This is referred to as a 'set' file.

A restore set file is also needed for recovery of original names.

The restore file is the same as the original two-column set file, but with the order of columns reversed. The first column of each file ***MUST*** be sorted alphabetically.

Set files for pseudonymization and recovery can be produced easily from many silos of data using wizards provided in IRI's GUI, *IRI Workbench*.

Set files are not specifically for names; they can be used as a list of any type of entity, but this example is specifically demonstrating names.

The *plankton* web services API must be 
hosted at the location specified in server_config.py (by default *http://localhost:8959*) and have both the *darkshield* and 
*darkshield-files* plugins installed. 

Python 3 must be installed, and the dependencies listed in the *requirements.txt* at the root of the repository must already be installed per the instructions in the *README.md* file at the root of the repository.

## Running the Demo

To execute, run `python pseudonymization.py`.

First, the *example.txt* file will be sent to the DarkShield API to have the names contained within pseudonymized. 

Next, the pseudonymized file will be sent to the DarkShield API to have the names restored using a **separate** masking context. 

All of the masking contexts and search contexts used in this demo are specified in the *setup.py* file.

The pseudonymized file will be placed in the *pseudo* directory, and the restored file will be placed in the *de-pseudo* directory.
