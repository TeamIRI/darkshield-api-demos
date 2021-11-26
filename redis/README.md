# DarkShield Files API: Redis

This example demonstrates the use of the *darkshield-files* API to search and 
mask items in a Redis database. 
For this demo I used a locally run Redis server.
To run, the *plankton* web services API must have the  *darkshield* and *darkshield-files* plugins installed.

To install the additional dependencies, execute *pip install -r requirements.txt* 
(make sure your virtual environment is activated, or your dependencies will 
be installed globally).

The example will find and mask the following:

1. Emails (EmailMatcher): Found using a regular expression and masked using a 
hashing function.
2. Social Security Numbers (SsnMatcher): Found using a regular expression and masked 
using redaction.
3. Names (NameMatcher): Found using a Named Entity Recognition (NER) model AND 
using format-specific json paths (all names can be found in the 'name' key/
tag, regardless of nesting).

To execute, run *python main.py*.

The results will be placed inside of the *redis-masked* directories.

The setup script will also download the NER and sentence detection models from the
[OpenNLP website](http://opennlp.sourceforge.net/models-1.5/) if not present in the
directory. If you are having trouble downloading the models, place the *en-ner-person.bin*
and *en-sent.bin* files into this directory.
