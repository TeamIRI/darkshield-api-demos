# DarkShield Files API: X12 Search/Masking

## Synopsis

This example demonstrates the use of the *darkshield-files* API to search for and 
mask sensitive data in ***ASC X12 EDI*** (*Accredited Standards Committee X12, Electronic Data Interchange*) files. 

## Requirements

To run, the *plankton* web services API must be hosted at 
the location specified in *server_config.py* (by default *http://localhost:8959*) with both the *darkshield* and *darkshield-files* 
plugins installed.

## Search Matchers and Masking Rules

The types of data to be searched for, and the masking rules to pair with each type of data, are defined in the *setup.py* file.

The types of data being searched for in this example include:

1. Names (NamesMatcher): Uses the Named Entity Recognition (NER) matcher to search for names. Additionally, a column matcher with the segment ID and column specified (e.g. N4\*2) is setup to match on names. 

The paired masking rule for each search matcher is format-preserving encryption (FPE).

## Execution 

To execute, run `python main.py`.

The results will be placed inside of the *x12-masked* directory.
