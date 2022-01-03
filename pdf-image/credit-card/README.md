# DarkShield Files API: Credit Card Images

This example demonstrates the use of the *darkshield-files* API to search and 
mask credit card numbers located on images of credit cards. To run, the *plankton* web services API 
must be hosted on the location specified in server_config.py (by default *http://localhost:8959*) and must have the *darkshield* and 
*darkshield-files* plugins installed.

To install the additional dependencies, execute *pip install -r requirements.txt* 
(make sure your virtual environment is activated, or your dependencies will 
be installed globally).

The *results.json* for each masked file will be placed inside of the *results*
folder.

The example will find and mask the following:

1. Credit Card Numbers (CcnMatcher): Found using a regular expression and masked using black box redaction.

To execute, run *python main.py*.
