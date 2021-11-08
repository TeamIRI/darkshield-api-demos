This example demonstrates the use of the darkshield-files API to search and mask JSON data in a CosmosDB database. To run, the plankton web services API must be hosted on http://localhost:8080 and must have the darkshield and darkshield-files plugins installed.

Additionally, an accessible instance of CosmosDB must be running. Credentials to access CosmosDB can be configured in the credentials.json file. URL of the CosmosDB resource, CosmosDB authorization key, name of container being searched, and name of container being written to.

The demo will read from one container and write the masked results to another container. Both the container being read from and container being written to need to be specified in the credentials.json file.

The example will find and mask the following:

Emails (EmailMatcher): Found using a regular expression and masked using a hashing function.

SSN Numbers (SSNMatcher): Found using a regular expression and masked using partial redaction.

Names (NameMatcher): Found using a Named Entity Recognition (NER) model AND using JSON paths (all names can be found in the 'name' key/tag, regardless of nesting).

To execute, run python main.py.

The setup script will also download the NER and sentence detection models from the OpenNLP website if not present in the directory. If you are having trouble downloading the models, place the en-ner-person.bin and en-sent.bin files into this directory.
