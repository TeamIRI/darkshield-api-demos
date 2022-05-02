# DarkShield Files API: Azure Containers

## Synopsis

This example demonstrates the use of the ***DarkShield Files API*** to search and mask files located in a container on Azure Blob Storage. 

## Requirements

To run, the DarkShield API must be hosted on the location specified in server_config.py (by default http://localhost:8959) with both the *darkshield* and *darkshield-files* plugins installed.

To install the additional dependencies, execute `pip install -r requirements.txt` (make sure your virtual environment is activated, or your dependencies will be installed globally).

Furthermore, you must have an Azure subscription (<https://azure.microsoft.com/en-us/free/>) and an Azure Blob storage account (<https://docs.microsoft.com/en-us/azure/storage/common/storage-account-overview>).

The setup script will also download the NER and sentence detection models from the OpenNLP website if not present in the parent directory. If you are having trouble downloading the models, place the *en-ner-person.bin*, *en-sent.bin*, and *en-token.bin* files into the parent directory.

To access a container in Azure Blob Storage you will need to initialize a client instance with a storage connection string. The connection string to your storage account can be found in the Azure Portal under the "Access Keys" section. Alternatively, you can use the DefaultAzureCredential. See 4a: Use blob storage with authentication (<https://docs.microsoft.com/en-us/azure/developer/python/azure-sdk-example-storage-use?tabs=cmd>).  

## Program Arguments

The masked files will be placed in a container you have indicated in your first argument during execution. If the container that is the destination of the masked files does not already exist, one will be created. Please note that in order to create a new container, the name used must not already be in use by someone else.

The program will take in a container name as the second argument and iterate over all blobs found there, sending each file to the API. 

You can include a prefix (e.g. ‘folder_name/’) as a third argument so only files and folders under a certain prefix will be searched and masked. 

A single file can also be specified by writing the full file path in place of a prefix.

The original and masked files are loaded fully in memory; for larger files that cannot be fit into memory the code needs to be modified to allow for a streaming solution.

The results.json received as a part of the response from the DarkShield API for each masked file will be placed inside the *results* folder.

## Data Search Matchers and Masking Rules

The example will find and mask the following:

***Countries***(*CountryMatcher*): Found using a list of entries called a "set file".

***Social Security Numbers***(*SsnMatcher*): Found using a regular expression and masked using format-preserving encryption.

***Emails*** (*EmailMatcher*): Found using a regular expression and masked using a hashing function.

***Names*** (*NameMatcher*): Found using a Named Entity Recognition (NER) model AND using format-specific json/xml paths (all names can be found in the 'name' key/tag, regardless of nesting).

## Running The Program

To execute, run `python main.py masked_container_name container_name folder_name_or_file_path` (folder_name_or_file_path is optional).

