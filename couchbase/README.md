# DarkShield API: Search/Masking Collections in CouchBase

This example demonstrates the use of the *darkshield* API to search and 
mask json collections in CouchBase.
To run, the *plankton* web services API must have the *darkshield* and *darkshield-files* plugins installed.

This demonstration will require:

1. A collection to read from and collection that will receive the masked json results. 
2. An index must be created for each collection (e.g. CREATE PRIMARY INDEX ON bucket.scope.collection).
3. Credentials for a user's account with access to the previously mentioned buckets
.
The example will find and mask the following:

1. Phone Numbers (PhoneMatcher): Found using a regular expression, masked with format-preserving AES256 encryption.
2. Emails (EmailMatcher): Found using a regular expression, masked with a SHA2 hash.
3. Names in context (NameMatcher): Uses a pre-trained NER model to find names in the context of a sentence, masks with format-preserving AES256 encryption.

To install the additional dependency for the CouchBase python SDK, execute *pip install -r requirements.txt* 
(make sure your virtual environment is activated, or the dependency will be installed globally).

To execute, run *python main.py* bucket_name scope_name collection_name to specify the target collection to query.
The results of masking operation will be upserted into a masked collection that has been specified in a credentials.json file
along with your CouchBase username and password.