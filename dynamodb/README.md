

We recommend that you download and host a [local dynamodb](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html) 
for testing purposes.

To install the additional dependencies, execute *pip install -r requirements.txt* 
(make sure your virtual environment is activated, or your dependencies will 
be installed globally).

Note that you should NOT use this code as is in production. Proper error handling
for DynamoDB needs to be added. See [here](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Programming.Errors.html)
for a detailed guide on how to implement it.
