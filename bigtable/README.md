# DarkShield API: Search/Masking text in Google Cloud Bigtable

## Synopsis

This example demonstrates the use of the DarkShield API to search and 
mask cells in Bigtable.

## Requirements

To run, the *plankton* web services API must be hosted at 
the location specified in *server_config.py* (by default *http://localhost:8959*) with both the *darkshield* and *darkshield-files* 
plugins installed.

To install the additional dependencies, execute `pip install -r requirements.txt`
(make sure your virtual environment is activated, or your dependencies will 
be installed globally).

The demo requires credentials and authentication to Google Cloud. The environment variable
*GOOGLE_APPLICATION_CREDENTIALS* may be set and pointed to a JSON file with credentials.

## Search Matchers and Masking Rules

The example will find and mask all of the following common sensitive data types with format-preserving encryption.

1.  Credit Cards (CcnMatcher): Found using a regular expression.
2.  Emails (EmailMatcher): Found using a regular expression.
3.  Names in context (NERMatcher): Uses a pre-trained NER model to find names in the context of a sentence.

## Execution
To execute, run `python main.py project_id instance_id`, where *project_id* is
your Cloud Platform project ID and *instance_id* is the ID of the Cloud Bigtable instance to connect to.

