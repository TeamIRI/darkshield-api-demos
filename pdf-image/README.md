# DarkShield Files API: PDF and Image Search/Masking

This example demonstrates the use of the *darkshield-files* API to search and 
mask pdf and image files. To run, the *plankton* web services API must be 
hosted on *http://localhost:8080* and must have the *darkshield* and 
*darkshield-files* plugins installed.

The example will search for and mask the two social security numbers in both
files using a function to redact the first 5 digits and apply format-preserving
encryption on the name (found using *names.set*).

Note that the image will apply a black box redaction for both the name and the
SSNs. The entire SSN will be black box redacted instead of a partial redaction,
since this is a function of *replace_chars* (note that there are ways of doing
partial redactions using regex pattern groups).

To execute, run *python main.py*.

The results will be placed inside of the *jpeg-masked* and *pdf-masked* directories.
