# DarkShield Files API: Check Image Test Data Generation

This example demonstrates the use of the *darkshield-files* API to replace names, addresses, and account numbers in images of checks with sample data. To run, the *plankton* web services API must be 
hosted on the location specified in server_config.py (by default *http://localhost:8959*) and must have the *darkshield* and 
*darkshield-files* plugins installed.

The example uses user-specified bounding boxes to define the regions where text will be replaced in the checks.
These coordinates can be interactively obtained through a page for bounding box matchers
in IRI Workbench.
This approach assumes that the information is in a consistent relative
position in the image.

For each bounding box, the portion of the image delimited by the bounds will be
replaced by text taken from an entry in a set file (a list of entries in a tab-separated values file).

To execute, run *python main.py*.

The results will be placed inside of the *check-gen* directory.
