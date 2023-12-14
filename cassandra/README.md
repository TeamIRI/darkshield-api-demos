# DarkShield API: Search/Masking text and blobs in Apache Cassandra

This example demonstrates the use of the *darkshield-nosql* API to search and 
mask values in Apache Cassandra.
An Apache Cassandra node must be accessible on the localhost at port 9042.
To run, the *plankton* web services API must be hosted on
the location specified in server_config.py (by default *http://localhost:8959*) and must have the *darkshield*,  *darkshield-files*, and *darkshield-nosql* 
plugins installed.

Additionally, an accessible instance of Cassandra must be running. Credentials to access Cassandra can be configured in the credentials.json file.

The example will find and mask the following:

1.  Phone Numbers (PhoneMatcher): Found using a regular expression, masked with format-preserving AES256 encryption.
2.  Emails (EmailMatcher): Found using a regular expression, masked with a SHA2 hash.
3.  Names in context (NameMatcher): Uses a pre-trained NER model to find names in the context of a sentence, masks with format-preserving AES256 encryption.

To install the additional dependency for the Casssandra Python driver, execute *pip install -r requirements.txt* 
(make sure your virtual environment is activated, or the dependency will 
be installed globally).

To execute, run *python main.py*.
