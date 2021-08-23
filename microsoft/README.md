# DarkShield Files API: Microsoft Office Document Search/Masking

This example demonstrates the use of the *darkshield-files* API to search and
mask Word (*.doc* and *.docx*) and Excel (*.xls* and *.xlsx*) documents. To run
the demo, the *plankton* web services API must be hosted on *http://localhost:8080*
and must have the *darkshield* and *darkshield-files* plugins installed.

The example will find and mask the following:

1. Account Number (AccountNumberMatcher): Found using a cell address regular expression
pattern to match on the *B* column inside of the *buyers* sheet.
2. Money (CurrencyMatcher): Found using a regular expression. A random offset is added
to the leading number using a *blur_int* function.
3. Names (NameMatcher): Found using a combination of Named Entity Recognition (NER)
and matching on the *name* column in the *buyers* sheet.
4. Emails (EmailMatcher): Found using a regular expression and masked using a hashing
function.
5. Phone Numbers (PhoneMatcher): Found using a regular expression and masked using
format-preserving encryption.
6. Social Security Numbers (SsnMatcher): Found using a regular expression pattern and
masked using format-preserving encryption.

Note that the *balance* column inside of *Bank Report.xlsx* will be masked as a
string instead of a formatted currency (internally represented in Excel as a floating-
point number), meaning that the line graph will no longer have valid input.
Future versions of DarkShield may introduce better conversion of strings to formatted
floating point numbers.

To execute, run *python main.py*.

The results will be placed inside of the *{file_name}-masked* directories for each
of the four files.
