# DarkShield Files API: DynamoDB

This example demonstrates the use of the *darkshield-files* API to search and 
mask items in a DynamoDB table. To run, the *plankton* web services API 
must be hosted on *http://localhost:8080* and must have the *darkshield* and 
*darkshield-files* plugins installed.

We recommend that you download and host a [local dynamodb](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html) 
for testing purposes.

To install the additional dependencies, execute *pip install -r requirements.txt* 
(make sure your virtual environment is activated, or your dependencies will 
be installed globally).

The setup script will also download the NER and sentence detection models from 
the [OpenNLP website](http://opennlp.sourceforge.net/models-1.5/) if not present 
in the parent directory. If you are having trouble downloading the models, place 
the *en-ner-person.bin*, *en-sent.bin*, and *en-token.bin* files into the 
parent directory.

The code will create a test table called *darkshield-test* inside of the DynamoDB
database and populate it with the contents of *data.json*. It will then scan all items 
inside of the table in batches, sending the data to be searched and masked to the API.
The masked batches are then inserted into a *darkshield-test-masked* table, while
the log files of the masking operations are stored inside of 
*results/batch{index}-results.json*.

The example will find and mask the following:

1. Emails (EmailMatcher): Found using a regular expression and masked using a 
hashing function.
2. Phone Numbers (PhoneMatcher): Found using a regular expression and masked 
using format-preserving encryption.
3. Names (NameMatcher): Found using a Named Entity Recognition (NER) model AND 
using format-specific json paths (all names can be found in the 'name' key/
tag, regardless of nesting).

To execute, run *python main.py url*. The script will use the *default*
profile in your AWS credentials file in order to access the bucket unless the
*--profile* flag is included. See the [boto3 quickstart guide](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration)
for more information on how to configure this file.

Note that you should NOT use this code as is in production. Modifications are needed
for Proper error handling in DynamoDB needs. See [here](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Programming.Errors.html)
for a detailed guide on how to implement it.
