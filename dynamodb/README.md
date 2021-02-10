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

The code will create a test table called *darkshield-test* inside of the DynamoDB
database and populate it with the contents of *data.json*. It will then scan all items 
inside of the table in batches, sending the data to be searched and masked to the API.
The masked batches are then inserted into a *darkshield-test-masked* table, while
the log files of the masking operations are stored inside of 
*results/batch{index}-results.json*.

Note that you should NOT use this code as is in production. Modifications are needed
for Proper error handling in DynamoDB needs. See [here](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Programming.Errors.html)
for a detailed guide on how to implement it.
