# DarkShield Files API: Image preprocessing pipeline

This example demonstrates the use of a set of procedures to preprocess images before sending to the *darkshield-files* API to search and 
mask. To run, the *plankton* web services API must be 
hosted on the location specified in server_config.py (by default *http://localhost:8959*) and must have the *darkshield* and 
*darkshield-files* plugins installed.

The example will search for and mask the two social security numbers in both
files using a function to redact the first 5 digits and apply format-preserving
encryption on the name (found using *names.set*).

Note that the image will apply a black box redaction for both the name and the
SSNs. The entire SSN will be black box redacted instead of a partial redaction,
since this is a function of *replace_chars* (note that there are ways of doing
partial redactions using regex pattern groups).

To execute, run *python main.py*, specifying one of the two: either a directory (with the -d flag) or a file (with the -f flag).
For example,
*python main.py -f "C:\Users\dakoz\Downloads\test-images\test-images\skew2.png"*
specifies a single file named *skew2.png* to process.

The results will be placed inside of the *masked* directory.
