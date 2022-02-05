# DarkShield Files API: Credit Card Number Image Generation

This example demonstrates the use of the *darkshield-files* API to place synthetic credit card numbers on images of credit cards. To run, the *plankton* web services API 
must be hosted on the location specified in server_config.py (by default *http://localhost:8959*) and must have the *darkshield* and 
*darkshield-files* plugins installed. It uses the 'OCR-A.ttf' custom font file to use as the font for the synthetic credit card numbers.

The synthetic image is placed in the *credit-card-gen* folder.

To install the additional dependencies, execute *pip install -r requirements.txt* 
(make sure your virtual environment is activated, or your dependencies will 
be installed globally).

To execute, run *python main.py*.
