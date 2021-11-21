# DarkShield Files API: CSV/TSV Search/Masking

This example demonstrates the use of the *darkshield-files* API to search and 
mask tabular (csv/tsv) files. To run, the *plankton* web services API must be 
hosted on the location specified in server_config.py (by default *http://localhost:8959*) and must have the *darkshield* and 
*darkshield-files* plugins installed.

The example will search and mask:
1. Emails (EmailsMatcher): regular expression pattern matcher with hashing rule. 
2. Names (NamesMatcher): Using a column matcher on any column ending with
'name', and a *Named Entity Recognition (NER)* matcher to search through the
*comment* field using a column filter (all names masked using Format Preserving 
encryption)

To execute, run *python main.py*.

The results will be placed inside of the *csv-masked* and *tsv-masked* 
directories.

Note that the csv appears more structured, while the tsv shows off some of the
more non-standard cases that DarkShield is capable of handling. Both will be
masked in the same manner.

The setup script will also download the NER and sentence detection models from 
the [OpenNLP website](http://opennlp.sourceforge.net/models-1.5/) if not present 
in the parent directory. If you are having trouble downloading the models, place 
the *en-ner-person.bin*, *en-sent.bin*, and *en-token.bin* files into the 
parent directory.
