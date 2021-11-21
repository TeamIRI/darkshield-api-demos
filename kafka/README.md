# DarkShield Files API: Kafka Message Search/Masking

This example demonstrates the use of the *darkshield-files* API to search and
mask json messages on a Kafka topic, and output masked messages and results
to separate topics. To run, the *plankton* web services API must be hosted on
*http://localhost:8959* and must have the *darkshield* and *darkshield-files*
plugins installed.

To install the additional dependencies, execute *pip install -r requirements.txt*
(make sure your virtual environment is activated, or your dependencies will
be installed globally).

Follow the [quickstart](https://kafka.apache.org/quickstart) guides to set up
a basic Kafka environment.

This demo uses three topics which have to be created:
* darkshield-demo
* darkshield-demo-masked
* darkshield-demo-results

You may wish to configure the retention time of the messages in the topics to
clean up the inboxes between demo runs.

A producer thread will be started to send the contents of *message.json* to the
*darkshield-demo* topic every 3 seconds. A consumer thread will pick up the
messages and send them to the API for search/masking. The masked message will
then be sent to the *darkshield-demo-masked* topic, while the *results.json*
audit log for the message will be sent to the *darkshield-demo-results* topic.

The example will find and mask the following:

1. Emails (EmailMatcher): Found using a regular expression and masked using a hashing
function.
2. Phone Numbers (PhoneMatcher): Found using a regular expression and masked using
format-preserving encryption.
3. Names (NameMatcher): Found using a Named Entity Recognition (NER) model AND using
format-specific json paths (all names can be found in the 'name' key/tag, regardless
of nesting).

To execute, run *python main.py*.

The results will be placed inside of the *text-masked* directory.
