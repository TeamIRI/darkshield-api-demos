![](http://www.iri.com/blog/wp-content/uploads/2020/07/iri-darkshield-logo-200px-high.png)

# DarkShield RPC API Demos

## Overview

This repository contains a collection of demo projects for the *DarkShield* and *DarkShield-Files* APIs, mostly using Python glue code.

## Requirements

The DarkShield API must be running and accessible through the network from the machine that is running any of these demos.

Python 3 must be installed on your system in order to execute any of the demos that use Python.

To start, it's recommended that you create an isolated Python 
[virtual environment](https://virtualenv.pypa.io/en/stable/) to avoid dependency 
bloat/clashes with your main system distribution.

To install the required dependencies, execute `pip install -r requirements.txt`
(make sure your virtual environment is activated, or your dependencies will 
be installed globally).

Some demo projects also contain a *requirements.txt* file for additional 
dependencies that need to be installed in order to run that particular demo.

## Configuration

The host and port that the DarkShield API server is hosted on may be specified in the *server_config.py* file.
Additionally, whether the server is using HTTPS or not may be specified.

## Execution

To execute the demos, refer to the instructions regarding the specific demo available in the *README.md* file
within the demo directory.
