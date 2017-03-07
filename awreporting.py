#!/usr/bin/env python

# Copyright 2017 - Gustavo Montamat
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
awreporting.py
AdWords API reporting script suitable for large scale reports.
"""

import argparse
import csv
import logging
import os
import Queue
import sys

from time import sleep

from accounts import get_account_ids
from reporting_threads import ReportDownloader, ReportDecompressor, END_SIGNAL

logger = logging.getLogger(__name__)

TEMP_DIR = 'temp'


def clear_dir(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except Exception as e:
            logger.exception("Couldn't create temporal directory.")
            sys.exit(1)
    for file_name in os.listdir(path):
        file_path = os.path.join(path, file_name)
        try:
            os.unlink(file_path)
        except Exception, e:
            logger.exception(
                u"Couldn't delete <{name}>".format(name=file_name)
            )


def read_query(query_file):
    try:
        with open(query_file, 'rb') as fin:
            query = fin.read().replace('\r', '').replace('\n', ' ')
    except Exception as e:
        logger.exception("Couldn't read query file.")
        sys.exit(1)
    return query


def merge_output(output, path):
    first = True
    with open(output, 'wb') as fout:
        csv_writer = csv.writer(fout, delimiter=',', quotechar='"')
        for file_name in os.listdir(path):
            if file_name[-4:] == '.csv':
                file_path = os.path.join(path, file_name)
                with open(file_path, 'rb') as fin:
                    csv_reader = csv.reader(fin, delimiter=',', quotechar='"')
                    if not first:
                        # Skip column headers
                        csv_reader.next()
                    first = False
                    for row in csv_reader:
                        csv_writer.writerow(row)


def get_report(token, query_file, output, threads, account_ids=None):
    logger.info("Preparing temporal directory.")
    clear_dir(TEMP_DIR)
    if not account_ids:
        logger.info("Retrieving all AdWords account ids.")
        account_ids = get_account_ids(token)
    logger.info("Loading AWQL query.")
    awql_query = read_query(query_file)
    # Create a queue with all the account ids
    queue_ids = Queue.Queue()
    [queue_ids.put(account_id) for account_id in account_ids]
    while True:
        queue_decompress = Queue.Queue()
        queue_fails = Queue.Queue()
        # Initialize two decompressor threads
        for i in xrange(2):
            report_decompressor = ReportDecompressor(
                queue_decompress, queue_fails, TEMP_DIR
            )
            report_decompressor.daemon = True
            report_decompressor.start()
        # Initialize downloader threads pool
        logger.info("Initializing ReportDownloader threads.")
        max_threads = min(queue_ids.qsize(), threads)
        for i in xrange(max_threads):
            if queue_ids.qsize() == 0:
                break
            report_downloader = ReportDownloader(
                token, queue_ids, queue_decompress, awql_query, TEMP_DIR
            )
            report_downloader.daemon = True
            report_downloader.start()
            sleep(0.1)
        logger.info("Used {thread_num} threads.".format(thread_num=i + 1))
        # Wait until all the account ids have been processed
        queue_ids.join()
        queue_ids.put(END_SIGNAL)
        # Wait until all gzipped reports have been extracted
        queue_decompress.join()
        queue_decompress.put(END_SIGNAL)
        if queue_fails.qsize() == 0:
            logger.info("All reports have been obtained.")
            break
        # Restart job with failed downloads
        queue_ids = Queue.Queue()
        [queue_ids.put(account_id) for account_id in queue_fails.get()]
    merge_output(output, TEMP_DIR)
    clear_dir(TEMP_DIR)


def main(token, query_file, output, threads):
    with open('run.log', 'w'):
        pass
    logging.basicConfig(
        filename='run.log', level=logging.WARNING,
        format=('%(asctime)s.%(msecs)03d\t%(threadName)s'
                '\t%(module)s.%(funcName)s\t%(levelname)s\t%(message)s'),
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    get_report(token, query_file, output, threads)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="PyAwReporting")
    parser.add_argument(
        '-o', '--output', help="Output file name", default='output.csv'
    )
    parser.add_argument(
        '-n', '--numthreads', help="Number of threads", type=int, default=10
    )
    required_arguments = parser.add_argument_group('required arguments')
    required_arguments.add_argument(
        '-t', '--token', help="AdWords YAML token file", required=True
    )
    required_arguments.add_argument(
        '-q', '--query', help="AWQL query file name", required=True
    )
    args = parser.parse_args()
    main(args.token, args.query, args.output, args.numthreads)
