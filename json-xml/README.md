# DarkShield Files API: JSON and XML Search/Masking

This example demonstrates the use of the *darkshield-files* API to search and mask json
and xml files. To run, the *plankton* web services API must be hosted on 
*http://localhost:8959* and must have the *darkshield* and *darkshield-files* plugins 
installed.

The example will find and mask the following:

1. Emails (EmailMatcher): Found using a regular expression and masked using a hashing
function.
2. Phone Numbers (PhoneMatcher): Found using a regular expression and masked using
format-preserving encryption.
3. Names (NameMatcher): Found using a Named Entity Recognition (NER) model AND using
format-specific json/xml paths (all names can be found in the 'name' key/tag, regardless
of nesting).

To execute, run *python main.py*.

The results will be placed inside of the *json-masked* and *xml-masked* directories.

The setup script will also download the NER and sentence detection models from the
[OpenNLP website](http://opennlp.sourceforge.net/models-1.5/) if not present in the
directory. If you are having trouble downloading the models, place the *en-ner-person.bin*
and *en-sent.bin* files into this directory.