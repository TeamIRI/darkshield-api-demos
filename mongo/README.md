# DarkShield Files API: Mongo Search/Masking

This example demonstrates the use of the *darkshield-files* API to search and mask json
documents from a Mongo collection. To run, the *plankton* web services API must be hosted on 
*http://localhost:8080* and must have the *darkshield* and *darkshield-files* plugins 
installed.

You must have a Mongo database installed and hosted on *http://localhost:27017*.

The script will create a *data* collection inside of the *darkshield* database if it
doesn't already exist. The data inserted resides in *data.json*.

The example will find and mask the following:

1. Emails (EmailMatcher): Found using a regular expression and masked using a hashing
function.
2. Phone Numbers (PhoneMatcher): Found using a regular expression and masked using
format-preserving encryption.
3. Names (NameMatcher): Found using a Named Entity Recognition (NER) model AND using
format-specific json paths (all names can be found in the 'name' key, regardless
of nesting).

To execute, run *python main.py*.

The results on the search/masking will be placed inside of the *results* directory. The
masked documents will be placed in the *darkshield.masked* collection. You can see the
masked documents by running the following from the command line:

    mongo
    use darkshield
    db.masked.find()

The setup script will also download the NER and sentence detection models from the
[OpenNLP website](http://opennlp.sourceforge.net/models-1.5/) if not present in the
directory. If you are having trouble downloading the models, place the *en-ner-person.bin*
and *en-sent.bin* files into this directory.