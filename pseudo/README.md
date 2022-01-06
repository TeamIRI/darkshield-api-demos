# DarkShield API: Pseudonymization and Restore
This demo demonstrates matching names based on a dictionary of names, consistently pseudonymizing names to other names, and restoring names to their original value.
To set up, a two-column, tab-separated file containing a list of names mapped to other names should be produced. A restore file is also needed for recovery of original names.
The restore file is the same as the original file, but with the orders of columns reversed. The first column of each file MUST be sorted alphabetically.
These 'set' files for pseudonymization and recovery can be produced easily from many silos of data using IRI's GUI, IRI Workbench.
Names will be searched and replaced with other names (consistently).
The pseudonymized file will then be sent to the DarkShield API for restoration of the original values, and the restored results will be put into a created *de-pseudo* directory.

To execute, run *python pseudonymization.py*.

The results will be placed inside of the *pseudo* and *de-pseudo* directories.
