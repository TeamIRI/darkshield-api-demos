# DarkShield Files API: CSV/TSV Search/Masking

This example demonstrates the use of the *darkshield-files* API to search and 
mask tabular (csv/tsv) files. To run, the *plankton* web services API must be 
hosted on *http://localhost:8080* and must have the *darkshield* and 
*darkshield-files* plugins installed.

The example will search and mask:
1. Emails (EmailsMatcher): regular expression pattern matcher with hashing rule. 
2. Names (NamesMatcher): Using a column matcher on any column ending with
'name', and a *Named Entity Recognition (NER)* matcher to search through the
*comment* field using a column filter (all names masked using Format Preserving encryption)

To execute, run *python main.py*.

The results will be placed inside of the *csv-masked* and *tsv-masked* 
directories.

Note that the csv appears more structured, while the tsv shows off some of the
more non-standard cases that DarkShield is capable of handling. Both will be
masked in the same manner.
