# DarkShield Files API: Image Preprocessing Pipeline

## Overview 

This example demonstrates the use of a set of procedures to preprocess images before sending to the *darkshield-files* API to search and 
mask. 

The DarkShield API uses Optical Character Recognition (OCR) to detect and recognize text in images.

In certain cases, preprocessing images can improve OCR accuracy, although techniques need to be adjusted on a per-image basis for the best results. 

This demo offers three different preprocessing techniques that adjust based on the properties of the particular image.

The techniques used in this demo include:

1. Rescaling
2. Adaptive thresholding binarization
3. Deskewing

The demo is not a 'one-size-fits-all' solution, but it does provide a template of how preprocessing can be integrated into a pipeline that involves sending images to the DarkShield API for searching and/or masking.

## Requirements

To run, the *plankton* web services API must be 
hosted at the location specified in server_config.py (by default *http://localhost:8959*) and have both the *darkshield* and 
*darkshield-files* plugins installed. 

Python 3 must be installed, and the dependencies listed in the *requirements.txt* at the root of the repository must already be installed per the instructions in the *README.md* file at the root of the repository.

## Search Matchers and Masking Rules Used

The specifications for what data to search for, and how to handle each type of data, are contained within the *setup.py* file.

This example will search for Social Security numbers and entries in a set (contained within the file *entries.set*).

Matches are redacted from the image with black boxes.

## Execution

To execute, run `python main.py`, specifying one of the two: either a directory (with the *-d* flag) or a file (with the *-f* flag).

For example,
`python main.py -f "C:\Users\dakoz\Downloads\test-images\test-images\skew2.png"`
specifies a single file named *skew2.png* to process.

A minimum skew angle and maximum width (in pixels) may be specified as arguments as well.

If the skew angle of the image is lower than the angle specified (if not specified, the default is 5 degrees), the deskewing
pipeline will not be used. 

If the width of the image is greater than the width specified (the default is 1600 pixels), the rescaling pipeline
will not be used.

The results will be placed inside of the *masked* directory.
