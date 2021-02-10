# DarkShield Files API: S3 Buckets

This example demonstrates the use of the *darkshield-files* API to search and 
mask files located on an S3 bucket. To run, the *plankton* web services API 
must be hosted on *http://localhost:8080* and must have the *darkshield* and 
*darkshield-files* plugins installed.

To install the additional dependencies, execute *pip install -r requirements.txt* 
(make sure your virtual environment is activated, or your dependencies will 
be installed globally).

The setup script will also download the NER and sentence detection models from 
the [OpenNLP website](http://opennlp.sourceforge.net/models-1.5/) if not present 
in the parent directory. If you are having trouble downloading the models, place 
the *en-ner-person.bin*, *en-sent.bin*, and *en-token.bin* files into the 
parent directory.

The program will take in a bucket name or an s3 url (starting with 's3://') and 
iterate over all objects found there, sending each file to the API. The s3 url can 
contain a prefix, which means only files under a certain prefix will be searched 
and masked. A single file can also be specified using its s3 url.

The original and masked files are loaded fully in memory, for larger files that
cannot be fit into memory the code needs to be modified to allow for a streaming 
solution (see comments in *main.py* for more information).

The masked files will be placed under the *masked* key in the root of the original 
bucket.

The *results.json* for each masked file will be placed inside of the *results*
folder.

The demo is best performed with test files obtained from the *json-xml* folder,
the *setup.py* code was copied from there.

The example will find and mask the following:

1. Emails (EmailMatcher): Found using a regular expression and masked using a 
hashing function.
2. Phone Numbers (PhoneMatcher): Found using a regular expression and masked 
using format-preserving encryption.
3. Names (NameMatcher): Found using a Named Entity Recognition (NER) model AND 
using format-specific json/xml paths (all names can be found in the 'name' key/
tag, regardless of nesting).

To execute, run *python main.py bucket_name_or_url*. The script will use the *default*
profile in your AWS credentials file in order to access the bucket unless the
*--profile* flag is included. See the [boto3 quickstart guide](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration)
for more information on how to configure this file.
