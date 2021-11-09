# DarkShield Files API: HL7 v2 Message Search/Masking

This example demonstrates the use of the *darkshield-files* API to search and 
mask text files. To run, the *plankton* web services API must be hosted on 
*http://localhost:8080* and must have the *darkshield* and *darkshield-files* 
plugins installed.

Names (NamesMatcher): Use the Named Entity Recognition (NER) matcher to search through the fields or can use a column matcher with the segment ID and column specified (e.g. PID|3) to mask target location using Format Preserving encryption.

To execute, run *python main.py*.

The results will be placed inside of the *hl7-masked* directory.
