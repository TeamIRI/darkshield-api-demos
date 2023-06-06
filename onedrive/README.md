# DarkShield Files API: OneDrive Online Searching/Masking

This example demonstrates the use of the darkshield-files API to search and mask files in OneDrive Online. To run, the plankton web services API must be hosted on <the location specified in server_config.py (by default http://localhost:8959)> and must have the darkshield and darkshield-files plugins installed.

Credentials to access the OneDrive Online site using Azure Active Directory must be configured in the config.json file.

The demo will read from either the entire file system or from with in a subfolder that has been specified as a parameter when executing the python program.

The example will find and mask the following:

Emails (EmailMatcher): Found using a regular expression and masked using a hashing function.

SSN Numbers (SSNMatcher): Found using a regular expression and masked using partial redaction.

To execute, run python main.py {subfolder_name} or python main.py.
