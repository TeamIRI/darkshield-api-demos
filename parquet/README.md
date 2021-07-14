# DarkShield Files API: Parquet Search/Masking

This example demonstrates the use of the *darkshield-files* API to search and mask Parquet files. 

This example requries DarkShield API version 1.2.0 or higher.

To run, the *plankton* web services API must be hosted on 
*http://localhost:8080* and must have the *darkshield* and *darkshield-files* plugins 
installed.

The example will find and mask the following:

1. Countries(CountryMatcher): Found using a list of entries called a "set file".
2. Social Security Numbers(SsnMatcher): Found using a regular expression and masked using
format-preserving encryption.
3. Names (NameMatcher): Found using a Named Entity Recognition (NER) model.

This may not include all of the possible sensitive data in the files, but it is what has been specified to search for this example.

To execute, run *python main.py*.

The results will be placed inside of the *parquet-masked* directory.

The setup script will also download the NER and sentence detection models from the
[OpenNLP website](http://opennlp.sourceforge.net/models-1.5/) if not present in the
directory. If you are having trouble downloading the models, place the *en-ner-person.bin*
and *en-sent.bin* files into this directory.