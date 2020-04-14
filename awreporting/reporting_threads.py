#!/usr/bin/env python

# Copyright 2020 - Gustavo Montamat
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
reporting_threads.py
Defines classes ReportDownloader and ReportDecompressor which download
and extract reports using the AdWords API.
"""

import csv
import gzip
import logging
import os
import threading

from socket import setdefaulttimeout
from ssl import SSLError
from time import sleep

from googleads.adwords import AdWordsClient
from googleads.errors import AdWordsReportError, GoogleAdsError

END_SIGNAL = '::END::'

ADWORDS_ERRORS_ABORT = [
    'AuthenticationError.CLIENT_CUSTOMER_ID_INVALID',
    'AuthenticationError.CUSTOMER_NOT_FOUND',
    'AuthorizationError.USER_PERMISSION_DENIED',
    'ReportDefinitionError.CUSTOMER_SERVING_TYPE_REPORT_MISMATCH',
    'QueryError'
]
ADWORDS_ERRORS_RETRY = [
    'ReportDownloadError.ERROR_GETTING_RESPONSE_FROM_BACKEND'
]
ADWORDS_ERRORS_WAIT = [
    'RateExceededError.RATE_EXCEEDED'
]


class ReportDownloader(threading.Thread):
    """Receives a queue with account ids and a query. Takes an account
    id from that queue and downloads its report using the AdWords API
    GetReportDownloader.
    """

    def __init__(self, token, queue_ids, queue_decompress, query, output_dir):
        threading.Thread.__init__(self)
        self.queue_ids = queue_ids
        self.queue_decompress = queue_decompress
        self.query = query
        self.output_dir = output_dir
        self.account_id = None
        while True:
            try:
                self.adwords_client = AdWordsClient.LoadFromStorage(token)
                break
            except IOError:
                sleep(0.1)
            except Exception as e:
                logging.exception("Couldn't initialize AdWordsClient.")

    def run(self):
        while True:
            self.account_id = self.queue_ids.get()
            if self.account_id != END_SIGNAL:
                self.adwords_client.SetClientCustomerId(self.account_id)
                self._download_report()
                self.queue_ids.task_done()
            else:
                # End signal was received
                self.queue_ids.task_done()
                self.queue_ids.put(END_SIGNAL)
                break

    def _download_report(self, max_retries=5):
        temp_name = '{id}.csv.gz'.format(id=self.account_id)
        output = os.path.join(self.output_dir, temp_name)
        setdefaulttimeout(900)
        # Initialize GetReportDownloader API service
        retries = 0
        while True:
            try:
                report_downloader = self.adwords_client.GetReportDownloader(version='v201809')
                break
            except Exception as e:
                logging.exception("API service error on {id}.".format(id=self.account_id))
                retries += 1
            if retries == max_retries:
                logging.critical("Ignoring account {id}.".format(id=self.account_id))
                return
        # Download gzipped report handling possible exceptions
        retries = 0
        while True:
            try:
                with open(output, 'wb') as fout:
                    report_downloader.DownloadReportWithAwql(
                        self.query, 'GZIPPED_CSV', fout, skip_report_header=True,
                        skip_column_header=False, skip_report_summary=True
                    )
                logging.info("Successfully downloaded <{name}>.".format(name=temp_name))
                # Queue up file for decompression
                self.queue_decompress.put(self.account_id)
                break
            except AdWordsReportError as e:
                logging.exception("AdWordsReportError on {id}.".format(id=self.account_id))
                if any(msg in e.message for msg in ADWORDS_ERRORS_ABORT):
                    retries = max_retries
                elif any(msg in e.message for msg in ADWORDS_ERRORS_RETRY):
                    retries += 1
                elif any(msg in e.message for msg in ADWORDS_ERRORS_WAIT):
                    sleep(e.retryAfterSeconds)
                else:
                    logging.critical("Unknown AdWordsReportError.")
                    retries += 1
            except GoogleAdsError as e:
                logging.exception("GoogleAdsError on {id}.".format(id=self.account_id))
                retries += 1
            except SSLError as e:
                logging.exception("SSLError on {id}.".format(id=self.account_id))
                retries += 1
            except Exception as e:
                logging.exception("Exception on {id}.".format(id=self.account_id))
                retries += 1
            if retries == max_retries:
                logging.critical("Ignoring account {id}.".format(id=self.account_id))
                try:
                    os.unlink(output)
                except Exception as e:
                    pass
                break


class ReportDecompressor(threading.Thread):
    """Receives a queue with account ids of completed downloads. Takes
    an account id and extracts its report. If the report is empty,
    deletes the extracted file.
    """

    def __init__(self, queue_decompress, queue_fails, output_dir):
        threading.Thread.__init__(self)
        self.queue_decompress = queue_decompress
        self.queue_fails = queue_fails  # Required if extraction fails
        self.output_dir = output_dir
        self.account_id = None

    def run(self):
        while True:
            self.account_id = self.queue_decompress.get()
            if self.account_id != END_SIGNAL:
                self._decompress_report()
                self.queue_decompress.task_done()
            else:
                # End signal received
                self.queue_decompress.task_done()
                self.queue_decompress.put(END_SIGNAL)
                break

    def _decompress_report(self):
        success = True
        empty = True
        temp_name = str(self.account_id) + '.csv.gz'
        output_name = str(self.account_id) + '.csv'
        input_file = os.path.join(self.output_dir, temp_name)
        output_file = os.path.join(self.output_dir, output_name)
        with gzip.open(input_file, mode='rt') as fin, open(output_file, 'w') as fout:
            csv_reader = csv.reader(fin, delimiter=',', quotechar='"')
            csv_writer = csv.writer(fout, delimiter=',', quotechar='"')
            # Obtain column headers
            csv_writer.writerow(next(csv_reader))
            try:
                for row in csv_reader:
                    csv_writer.writerow(row)
                    empty = False
            except Exception as e:
                logging.exception("Error extracting <{name}>.".format(name=temp_name))
                success = False
        if empty or not success:
            try:
                os.unlink(output_file)
            except Exception as e:
                logging.exception("Error deleting <{name}>.".format(name=output_name))
        try:
            os.unlink(input_file)
        except Exception as e:
            logging.exception("Error deleting <{name}>.".format(name=temp_name))
        if not success:
            self.queue_fails.put(self.account_id)
