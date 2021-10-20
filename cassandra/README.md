# DarkShield API: Search/Masking text and blobs in Apache Cassandra

This example demonstrates the use of the *darkshield* API to search and 
mask values in Apache Cassandra.
An Apache Cassandra node must be accessible on the localhost at port 9042.
To run, the *plankton* web services API must be hosted on
*http://localhost:8080* and must have the *darkshield* and *darkshield-files*
plugins installed.

The example will find and mask the following:

1.  Phone Numbers (PhoneMatcher): Found using a regular expression, masked with format-preserving AES256 encryption.
2.  Emails (EmailMatcher): Found using a regular expression, masked with a SHA2 hash.
3.  Names in context (NameMatcher): Uses a pre-trained NER model to find names in the context of a sentence, masks with format-preserving AES256 encryption.

To install the additional dependency for the Casssandra Python driver, execute *pip install -r requirements.txt* 
(make sure your virtual environment is activated, or the dependency will 
be installed globally).

To execute, run *python main.py*.
Masked and original versions of the blob (which is a PDF documentin this case) will be written to the *masked* folder,
along with the JSON results returned as a part of the response from the DarkShield Files API.
