![](http://www.iri.com/blog/wp-content/uploads/2020/07/iri-darkshield-logo-200px-high.png)
# DarkShield RPC API Demos
A collection of demo projects for the *DarkShield* and *DarkShield-Files* APIs
using Python glue code.

You need to have Python 3 installed on your system in order to execute these demos.

To start, it's recommended that you create an isolated Python 
[virtual environment](https://virtualenv.pypa.io/en/stable/) to avoid dependency 
bloat/clashes with your main system distribution.

To install the required dependencies, execute *pip install -r requirements.txt* 
(make sure your virtual environment is activated, or your dependencies will 
be installed globally).

Some demo projects also contain a *requirements.txt* file for additional 
dependencies that need to be installed in order to run that particular demo.

To execute the demos, refer to the instructions regarding the specific demo available in the *README.md* file
within the demo directory.

The host and port that the DarkShield API server is hosted on may be specified in the *server_config.py* file.
Additionally, whether the server is using HTTPS or not may be specified.
