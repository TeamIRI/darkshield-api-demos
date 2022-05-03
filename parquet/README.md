# DarkShield Files API: Parquet Search/Masking

## Synopsis

This example demonstrates the use of the DarkShield API to search and mask Parquet files.

## Requirements

This example requires DarkShield API version 1.2.0 or higher.

The *plankton* web services API must be hosted at
the location specified in *server_config.py* (by default *http://localhost:8959*) with both the *darkshield* and *darkshield-files* plugins
installed.

## Search Matchers and Masking Rules

Specifications for matching on sensitive data and pairing with a masking rule are contained in the configurable *setup.py* file.

The example will find and mask the following:

1. Countries(CountryMatcher): Found using a list of entries contained in a "set file".
2. Social Security Numbers(SsnMatcher): Found using a regular expression and masked using
format-preserving encryption.
3. Names (NameMatcher): Found using a Named Entity Recognition (NER) model.


Note that this does not include all of the data that could possibly be considered sensitive in the files; it is only what has been explicitly specified to search for in this example. 

What is considered sensitive is fully up to the discretion of the user and is denoted by creating a search context to match on data with search matchers.

## Execution

To execute, run `python main.py`.

The results will be placed inside of the *parquet-masked* directory.

The setup script will also download the NER and sentence detection models from
the [OpenNLP website](http://opennlp.sourceforge.net/models-1.5/) if not present
in the parent directory. 

If you are having trouble downloading the models, place
the *en-ner-person.bin* and *en-sent.bin* files into the parent directory.
