# PyAwReporting

## Important Note

This is neither an official [AdWords API](https://developers.google.com/adwords/api/) repository nor a clone of [AwReporting](https://github.com/googleads/aw-reporting). Consider using [AwReporting](https://github.com/googleads/aw-reporting) if you are a Java developer.

Useful links:
* https://developers.google.com/adwords/api/
* https://github.com/googleads/googleads-python-lib
* https://github.com/googleads/aw-reporting

## Overview

[PyAwReporting](https://github.com/gmontamat/pyaw-reporting) is an open-source Python 2.7 framework suitable for large scale AdWords API reporting.
Output reports are comma-separated values (CSV) plaintext files. By default, the script uses 10 threads to download a report for each account. The number of threads used can be modified using the *-n* parameter.

## Quick Start

### Prerequisites

You will need Python 2.7 with the [googleads](https://pypi.python.org/pypi/googleads) package installed (using a virtualenv is recommended). An access token *YAML* file with the corresponding AdWords credentials is also needed. The optional parameter **client\_customer\_id** is required in the *YAML* file, you should enter your AdWords Manager Account (formerly MCC) id. For The file *example.yaml* shows how your token should look like. Report [AWQL](https://developers.google.com/adwords/api/docs/guides/awql) queries should be stored in a plaintext file and passed to the script using the *-q* parameter. There is an example query in the file *query.txt*. For more information about report types refer to [Report Types](https://developers.google.com/adwords/api/docs/appendix/reports).

### Installation

<code>$ pip install googleads</code>

<code>$ git clone https://github.com/gmontamat/pyaw-reporting</code>

### Usage

<code>$ python awreporting.py -t YAML_TOKEN_FILE -q AWQL_QUERY_FILE [-o OUTPUT_NAME] [-n NUMBER_OF_THREADS]</code>

For example:

<code>$ python awreporting.py -t example.yaml -q query.txt -o adperformance.csv -n 100</code>
