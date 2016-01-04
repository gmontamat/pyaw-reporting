# PyAwReporting

## Important Note

This is not an official [AdWords API](https://developers.google.com/adwords/api/) repository nor a clone of [AwReporting](https://github.com/googleads/aw-reporting).
Consider using [AwReporting](https://github.com/googleads/aw-reporting) if you are a Java developer.

Useful links:
* https://developers.google.com/adwords/api/
* https://github.com/googleads/googleads-python-lib
* https://github.com/googleads/aw-reporting

## Overview

[PyAwReporting](https://github.com/gmontamat/pyaw-reporting) is an open-source Python 2.7 script suitable for large scale AdWords API reporting.
Output reports are comma-separated values (CSV) files in plain text. By default, the script uses 10 threads to download a report for each account and the number of threads used can be overwritten using the *-n* parameter.

## Quick Start

### Prerequisites

You will need Python 2.7 with the [googleads](https://pypi.python.org/pypi/googleads) package installed (using a virtualenv is recommended). An access token YAML file with the corresponding AdWords credentials is required. The optional parameter **client\_customer\_id** is required in the YAML with the AdWords Manager Account (formerly MCC) id. Report [AWQL](https://developers.google.com/adwords/api/docs/guides/awql) queries should be stored in a plaintext file and passed to the script using the *-q* parameter. See the attached example files for reference.

### Installation

<code>$ pip install [--upgrade] googleads</code>

<code>$ git clone https://github.com/gmontamat/pyaw-reporting</code>

### Usage

<code>$ python awreporting.py -t YAML_TOKEN_FILE -q AWQL_QUERY_FILE [-o OUTPUT_NAME] [-n NUMBER_OF_THREADS]</code>

For example:

<code>$ python awreporting.py -t example.yaml -q query.txt -o adperformance.csv -n 100</code>
