# DarkShield Files API: JSON and XML Search/Masking using Passphrase obtained from Azure Key Vault.

This example demonstrates the use of the *darkshield-files* API to search and mask json
and xml files, interacting with Azure Key Vault to obtain the encryption passphrase. To run, the *plankton* web services API must be hosted on 
*http://localhost:8080* and must have the *darkshield* and *darkshield-files* plugins 
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


To execute, run *python main.py*.

The results will be placed inside of the *json-masked-key-vault* and *xml-masked-key-vault* directories.

The setup script will also download the NER and sentence detection models from the
[OpenNLP website](http://opennlp.sourceforge.net/models-1.5/) if not present in the
directory. If you are having trouble downloading the models, place the *en-ner-person.bin*
and *en-sent.bin* files into this directory.