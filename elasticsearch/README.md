# DarkShield Files API: Elasticsearch Search/Masking

This example demonstrates the use of the *darkshield-files* API to search and mask JSON
documents from a local Elasticsearch instance. To run, the *plankton* web services API must be hosted on 
the location specified in server_config.py (by default *http://localhost:8959*) and must have the *darkshield* and *darkshield-files* plugins 
installed.

You must have Elasticsearch installed and hosted locally at the default port.

To install the additional dependencies, execute *pip install -r requirements.txt* 
(make sure your virtual environment is activated, or your dependencies will 
be installed globally).

The example will load two JSON documents into an index called *test-index*.
The index will have its contents searched and masked by the DarkShield API and sent to a new index
called *test-index-masked*.
The masked contents in *test-index-masked* will be searched for and displayed by the program.

DarkShield will find and mask the following:

1. Emails (EmailMatcher): Found using a regular expression and masked using a hashing
function.
2. Phone Numbers (PhoneMatcher): Found using a regular expression and masked using
format-preserving encryption.
3. Names (NameMatcher): Found using a Named Entity Recognition (NER) model AND using
format-specific json paths (all names can be found in the 'name' key, regardless
of nesting).

To execute, run *python main.py*.

The setup script will also download the NER and sentence detection models from 
the [OpenNLP website](http://opennlp.sourceforge.net/models-1.5/) if not present 
in the parent directory. If you are having trouble downloading the models, place 
the *en-ner-person.bin* and *en-sent.bin* files into the parent directory.