# DarkShield Files API: JSON and XML Search/Masking using Passphrase obtained from Azure Key Vault.
## Demo 1 (main.py):
This example demonstrates the use of the *darkshield-files* API to search and mask json
and xml files, interacting with Azure Key Vault to obtain the encryption passphrase. To run, the *plankton* web services API must be hosted on 
the location specified in server_config.py (by default *http://localhost:8959*) and must have the *darkshield* and *darkshield-files* plugins 
installed.

The environment variables 'KEY_VAULT_NAME' and 'SECRET_NAME' must be set to the name of
the key vault and secret, respectively, that the encryption passphrase should be obtained from.

The example will find and mask all of the following with format-preserving encryption 
that utilizes the 'secret' obtained from the Key Vault as the encryption passphrase:

1. Credit Cards (CcnMatcher): Found using a regular expression and validated with JavaScript validator script.
2. Dates (DateMatcher): American date format; found using a regular expression.
3. Emails (EmailMatcher): Found using a regular expression.
4. IP Addresses (IpAddressMatcher): Found using a regular expression.
5. Names (NameMatcher): Uses a pre-trained NER model to find names in the context of a sentence.
6. Phone Numbers (PhoneMatcher): Found using a regular expression.
7. Social Security Numbers (SsnMatcher): Found using a regular expression.
8. URLs (URLMatcher): Found using a regular expression.
9. US Zip Codes (USZipMatcher): Found using a regular expression.
10. Vehicle Identification Numbers (VINMatcher): Found using a regular expression and validated with a JavaScript validator script.


To execute, run *python main.py*. Optionally, the version of the secret to obtain from Azure Key Vault that is used 
as the encryption passphrase may be specified as an argument with a *-v* flag. If no version for the secret is specified,
the latest version will be used.

The results will be placed inside of the *json-masked-key-vault* and *xml-masked-key-vault* directories.

The setup script will also download the NER and sentence detection models from the
[OpenNLP website](http://opennlp.sourceforge.net/models-1.5/) if not present in the
directory. If you are having trouble downloading the models, place the *en-ner-person.bin*
and *en-sent.bin* files into this directory.

## Demo 2 (Encrypt_Decrypt.py):
This example demonstrates the use of the *darkshield-files* API to encrypt all values in a JSON file converted from an HL7 message that have a key 
of 'firstName' or 'lastName' using an encryption passphrase obtained from Azure Key Vault.

The resulting masked file is then sent 
back to the DarkShield API for decryption using a separate context that is set up for decryption and matches on the same JSON keys. 

The passphrase for decryption is obtained from Azure Key Vault as well. The passphrase used for decryption must match the one used for 
encryption in order to get the correct decrypted result. The passphrase is obtained from Azure Key Vault using the key vault name 
and the secret name. 

In this demo, no argument for version of the secret is specified, so the secret obtained is the latest.

To execute, run *python Encrypt_Decrypt.py*. Optionally, the version of the secret to obtain from Azure Key Vault that is used 
as the encryption passphrase may be specified as an argument with a *-v* flag. If no version for the secret is specified,
the latest version will be used.

The results will be placed inside of the *encrypted-key-vault* and *decrypted-key-vault* directories.
