# DarkShield Files API: Elasticsearch Search/Masking

This example demonstrates the use of the *darkshield-nosql* API to search and mask JSON
documents from a local Elasticsearch instance. To run, the *plankton* web services API must be hosted on 
the location specified in server_config.py (by default *http://localhost:8959*) and must have the *darkshield*,  *darkshield-files*, and *darkshield-nosql* 
plugins installed.

Additionally, an accessible instance of Elasticsearch must be running. Credentials to access Elasticsearch can be configured in the credentials.json file.

To install the additional dependencies, execute *pip install -r requirements.txt* 
(make sure your virtual environment is activated, or your dependencies will 
be installed globally).

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