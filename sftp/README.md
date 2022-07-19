# DarkShield Files API: Searching and Masking Files Through SFTP

## Synopsis

This example demonstrates the use of the *darkshield-files* API to search and mask files accessed through [SFTP](https://www.ssh.com/academy/ssh/sftp).

## Requirements

The *plankton* web services API must be hosted at
the location specified in *server_config.py* (by default *http://localhost:8959*) with both the *darkshield* and *darkshield-files* plugins 
installed. Install Python dependencies by running the command `pip install -r requirements.txt`.

## Arguments
The program accepts the following arguments through command-line flags.

1. -H Specify the hostname to access.
2. -u Specify the username for the hostname.
3. -p Specify the password for the user.
4. -r Specify a path to the remote file to access.

All arguments are required.

For example: `python main.py -H MyServer -u myUser -p myPassword -r myRemotePath`

## Search Matchers and Masking Rules

The example will find and mask the following, as specified in *setup.py*:

1. Emails (EmailMatcher): Found using a regular expression and masked using a hashing
function.
2. Phone Numbers (PhoneMatcher): Found using a regular expression and masked using
format-preserving encryption.
3. Names (NameMatcher): Found using a Named Entity Recognition (NER) model AND using
format-specific json/xml paths (all names can be found in the 'name' key/tag, regardless
of nesting).

## Execution

To execute, run `python main.py`.

The results will be placed inside of the *masked* directory.

The setup script will also download the NER and sentence detection models from the
[OpenNLP website](http://opennlp.sourceforge.net/models-1.5/) if not present in the
directory. If you are having trouble downloading the models, place the *en-ner-person.bin*
and *en-sent.bin* files into this directory.
