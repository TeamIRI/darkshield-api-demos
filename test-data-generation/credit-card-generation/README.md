# DarkShield Files API: Credit Card Number Image Generation

## Synopsis

This example demonstrates the use of the *darkshield-files* API to place synthetic credit card numbers on images of credit cards.

## Requirements

To run, the DarkShield API 
must be hosted at the location specified in *server_config.py* (by default *http://localhost:8959*) with both the *darkshield* and 
*darkshield-files* plugins installed. 

Python 3 must be installed along with the common Python dependencies that are shared by all demos in this repository (specified in the root *requirements.txt* file).

This example uses the 'OCR-A.ttf' custom font file as the font for the synthetic credit card numbers.

## Execution

To execute, run `python main.py`.

The synthetic images are placed in the *credit-card-gen* folder.
