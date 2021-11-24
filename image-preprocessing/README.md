# DarkShield Files API: Image preprocessing pipeline

This example demonstrates the use of a set of procedures to preprocess images before sending to the *darkshield-files* API to search and 
mask. To run, the *plankton* web services API must be 
hosted on the location specified in server_config.py (by default *http://localhost:8959*) and must have the *darkshield* and 
*darkshield-files* plugins installed.

The example will search for Social Security numbers and entries in a set (found using *entries.set*).
Matches are redacted from the image with black boxes.

To execute, run *python main.py*, specifying one of the two: either a directory (with the -d flag) or a file (with the -f flag).
For example,
*python main.py -f "C:\Users\dakoz\Downloads\test-images\test-images\skew2.png"*
specifies a single file named *skew2.png* to process.

A minimum skew angle and maximum width (in pixels) may be specified as arguments as well.
If the skew angle of the image is lower than the angle specified (if not specified, the default is 5 degrees), the deskewing
pipeline will not be used. If the width of the image is greater than the width specified (the default is 1600 pixels), the rescaling pipeline
will not be used.

The results will be placed inside of the *masked* directory.
