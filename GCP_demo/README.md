This example demonstrates the use of the darkshield-files API to search and mask files located in a bucket on Google Cloud Storage. To run, the plankton web services API must be hosted on http://localhost:8080 and must have the darkshield and darkshield-files plugins installed.

To install the additional dependencies, execute pip install -r requirements.txt (make sure your virtual environment is activated, or your dependencies will be installed globally). Furthermore, a service account must be created in Google Cloud.

The setup script will also download the NER and sentence detection models from the OpenNLP website if not present in the parent directory. If you are having trouble downloading the models, place the en-ner-person.bin, en-sent.bin, and en-token.bin files into the parent directory.

The masked files will be placed in a bucket you have indicated in your first argument during execution. If the bucket that is the destination of the masked files does not already exist one will be created. Please note that to create a new bucket the name used must not already be in use by someone else.

The program will take in a bucket name as the second argument and iterate over all blobs found there, sending each file to the API. You can include a prefix (e.g. ‘folder_name/’) as a third argument so only files and folders under a certain prefix will be searched and masked.  A single file can also be specified by writing the full file path in place of a prefix.

The original and masked files are loaded fully in memory, for larger files that cannot be fit into memory the code needs to be modified to allow for a streaming solution.

The results.json for each masked file will be placed inside the results folder.

The example will find and mask the following:

Countries(CountryMatcher): Found using a list of entries called a "set file".
    
Social Security Numbers(SsnMatcher): Found using a regular expression and masked using format-preserving encryption.
    
Emails (EmailMatcher): Found using a regular expression and masked using a hashing function.
    
Names (NameMatcher): Found using a Named Entity Recognition (NER) model AND using format-specific json/xml paths (all names can be found in the 'name' key/tag, regardless of nesting).

To execute, run python main.py masked_bucket_name bucket_name folder_name_or_file_path (folder_name_or_file_path is optional). To access a bucket in Google Cloud Storage the script will use a credentials json file that was generated when you created your service account. Follow the instructions in the Setting the environment variable section (https://cloud.google.com/docs/authentication/getting-started) so your application’s code can access the authentication credentials.
