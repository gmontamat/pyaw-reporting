# PyAwReporting

An AdWords API large scale reporting tool written in Python. Reports are downloaded as plaintext files but connectivity with a database engine such as MySQL, PostgreSQL, or MongoDB can be implemented upon request.

## Important notes

This is neither an official [AdWords API](https://developers.google.com/adwords/api/) repository nor a clone of [AwReporting](https://github.com/googleads/aw-reporting). Consider using [AwReporting](https://github.com/googleads/aw-reporting) if you are a Java developer.

When using this tool it is necessary to enable a DNS cache in your system, such as [nscd](http://man7.org/linux/man-pages/man8/nscd.8.html). This should eliminate DNS lookup problems when repeatedly calling the AdWords API server. In some Linux systems nscd is not enabled by default but it can be started with:

<code># systemctl start nscd</code>

## Useful links

* https://developers.google.com/adwords/api/
* https://github.com/googleads/googleads-python-lib
* https://github.com/googleads/aw-reporting

## Overview

[PyAwReporting](https://github.com/gmontamat/pyaw-reporting) is an open-source Python 2.7 framework suitable for large scale AdWords API reporting.
Output reports are comma-separated values (CSV) plaintext files. By default, the script uses 10 threads to download reports simultaneously from different accounts. The number of threads used can be modified using the *-n* parameter. It has been successfully tested using +100 threads making it useful for heavy load AdWords Manager Accounts.

## Supported API version

The latest version supported by this program is [v201708](http://googleadsdeveloper.blogspot.com/2017/08/announcing-v201708-of-adwords-api.html) with [googleads 7.0.0](https://pypi.python.org/pypi/googleads). Previous versions of the API are not supported.

## Quick Start

### Prerequisites

You will need Python 2.7 with the [googleads](https://pypi.python.org/pypi/googleads) package installed (using a virtualenv is recommended). An access token *YAML* file with the corresponding AdWords credentials is also needed. The optional parameter **client\_customer\_id** must be included in the *YAML* file, you should enter your AdWords Manager Account (formerly MCC) id. This way, all the AdWords accounts linked to the Manager Account will be retrieved. The file *example.yaml* shows how your token should look like. Report [AWQL](https://developers.google.com/adwords/api/docs/guides/awql) queries should be stored in a plaintext file and passed to the script using the *-q* parameter. There is an example query in the file *query.txt* which will retrieve clicks and impressions per ad for the last 7 days. For more information about report types refer to [Report Types](https://developers.google.com/adwords/api/docs/appendix/reports).

### Installation

<code>$ pip install googleads</code>

<code>$ git clone https://github.com/gmontamat/pyaw-reporting</code>

### Usage

<code>$ python awreporting.py -t YAML_TOKEN_FILE -q AWQL_QUERY_FILE [-o OUTPUT_NAME] [-n NUMBER_OF_THREADS]</code>

For example:

<code>$ python awreporting.py -t example.yaml -q query.txt -o adperformance.csv -n 100</code>

### Notes

The example token file provided (*example.yaml*) is not valid. Refer to [this guide](https://developers.google.com/adwords/api/docs/guides/first-api-call) if you are using the AdWords API for the first time. We recommend to start with a small number of threads (the default is 10) and increase it accordingly. The AdWords server may complain when many API calls are made at the same time but those exceptions are handled by the app.

If you find many <code>URLError: <urlopen error [Errno -2] Name or service not known></code> in your logs, enable a DNS cache in your system.
