# DarkShield Files API: Solr Search/Masking

This example demonstrates the use of the *darkshield-files* API to search and mask JSON
documents from a Solr collection. To run, the *plankton* web services API must be running
with the *darkshield* and *darkshield-files* plugins installed.

You must have Solr installed and accessible through the network.

DarkShield will find and mask the following:

1. Emails (EmailMatcher): Found using a regular expression and masked using a hashing
function.
2. Phone Numbers (PhoneMatcher): Found using a regular expression and masked using
format-preserving encryption.
3. Names (NameMatcher): Found using a Named Entity Recognition (NER) model AND using
format-specific json paths (all names can be found in the 'name' key, regardless
of nesting).

The search and mask contexts are handled in *setup.py* and can be manually modified
to change the types of data to match against, along with the masking rules to use
for each type of data.
File search and mask contexts are handled in *setup.py* as well. These allow for
file format-specific matchers and configuration options.

To execute, run *python main.py*.

Some optional arguments may be specified as follows:
  -h, --help            show help message and exit
  --collection_name COLLECTION_NAME
                        The collection to search and mask.
  --host HOST           The host of Solr.
  --port PORT           The port of Solr.
  --query QUERY         The search query to use.
  --rows ROWS           The number of rows to limit query results to.
  
The setup script will also download the NER and sentence detection models from 
the [OpenNLP website](http://opennlp.sourceforge.net/models-1.5/) if not present 
in the parent directory. If you are having trouble downloading the models, place 
the *en-ner-person.bin* and *en-sent.bin* files into the parent directory.
