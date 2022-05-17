# DarkShield Files API: File Search/Masking through Interactive File Picker

![Searching and Masking Files through Interactive File Browser](filepicker-masking.gif)

## Synopsis

This example demonstrates the use of the DarkShield API to search and 
mask files picked through a file browser. 

## Requirements

To run, the *plankton* web services API must be hosted at 
the location specified in *server_config.py* (by default *http://localhost:8959*) with both the *darkshield* and *darkshield-files* 
plugins installed.

Python 3 must be installed.

The dependencies specified in the root *requirements.txt* file must be installed with `pip install -r requirements.txt`.

## Search Matchers and Masking Rules

The example will find and mask all of the following common sensitive data types with format-preserving encryption.

1.  Credit Cards (CcnMatcher): Found using a regular expression and validated with JavaScript validator script.
2.  Dates (DateMatcher): American date format; found using a regular expression.
3.  Emails (EmailMatcher): Found using a regular expression.
4.  IP Addresses (IpAddressMatcher): Found using a regular expression.
5.  First Names (FirstNameMatcher): Found using a set of entries called a 'set file'. 
    The entries include 2000 common first names. Configuration set to only accept full matches, and ignore case differences.
6.  Last Names (LastNameMatcher): Found using a set of entries called a 'set file'.
    The entries include 1000 common last names. Configuration set to only accept full matches, and ignore case differences.
7.  Names in context (NERMatcher): Uses a pre-trained NER model to find names in the context of a sentence.
8.  Phone Numbers (PhoneMatcher): Found using a regular expression.
9.  Social Security Numbers (SsnMatcher): Found using a regular expression.
10. URLs (URLMatcher): Found using a regular expression.
11. US Zip Codes (USZipMatcher): Found using a regular expression.
12. Vehicle Identification Numbers (VINMatcher): Found using a regular expression and validated with a JavaScript validator script.

The specifications for these matchers and masking rules are contained in *setup.py* and can be modified.

## Execution

To execute, run `python main.py`.

The results will be placed inside of the *masked* directory.

The example will continue to run so long as a file is picked.
