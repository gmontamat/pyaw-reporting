#!/usr/bin/env python

# Copyright 2019 - Gustavo Montamat
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
try:
    import Queue as queue
except ImportError as e:
    import queue
import shutil
import tempfile

from time import sleep

from accounts import get_account_ids
from reporting_threads import ReportDownloader, ReportDecompressor, END_SIGNAL


def read_query(query_file):
    if os.path.isfile(query_file):
        logging.error("Query file <{}> does not exist.".format(query_file))
        return
    try:
        with open(query_file, 'r') as fin:
            query = fin.read().replace('\r', '').replace('\n', ' ')
    except Exception as e:
        logging.exception("Could not read query file.")
        return
    return query


def merge_output(output, path):
    first = True
    with open(output, 'w') as fout:
        csv_writer = csv.writer(fout, delimiter=',', quotechar='"')
        for file_name in os.listdir(path):
            if file_name[-4:] == '.csv':
                file_path = os.path.join(path, file_name)
                with open(file_path, 'r') as fin:
                    csv_reader = csv.reader(fin, delimiter=',', quotechar='"')
                    if not first:
                        next(csv_reader, None)  # Skip headers
                    else:
                        first = False
                    for row in csv_reader:
                        csv_writer.writerow(row)


def get_report(token, awql_query, output, threads, account_ids=None):
    if account_ids is None:
        logging.info("Retrieving all AdWords account ids.")
        account_ids = get_account_ids(token)
    if not account_ids:
        logging.error("No account ids where found. Check token.")
        return
    logging.info("Creating temporal directory.")
    temporal_path = tempfile.mkdtemp()
    # Create a queue with all the account ids
    queue_ids = queue.Queue()
    [queue_ids.put(account_id) for account_id in account_ids]
    while True:
        queue_decompress = queue.Queue()
        queue_fails = queue.Queue()
        # Initialize two decompressor threads
        logging.info("Starting ReportDecompressor threads.")
        for i in range(2):
            report_decompressor = ReportDecompressor(
                queue_decompress, queue_fails, temporal_path
            )
            report_decompressor.daemon = True
            report_decompressor.start()
        # Initialize downloader threads pool
        logging.info("Starting ReportDownloader threads.")
        max_threads = min(queue_ids.qsize(), threads)
        for i in range(max_threads):
            if queue_ids.qsize() == 0:
                break
            report_downloader = ReportDownloader(
                token, queue_ids, queue_decompress, awql_query, temporal_path
            )
            report_downloader.daemon = True
            report_downloader.start()
            sleep(0.1)
        logging.info("Used {thread_num} threads.".format(thread_num=i + 1))
        # Wait until all the account ids have been processed
        queue_ids.join()
        queue_ids.put(END_SIGNAL)
        # Wait until all gzipped reports have been extracted
        queue_decompress.join()
        queue_decompress.put(END_SIGNAL)
        if queue_fails.qsize() == 0:
            break
        # Restart job with failed downloads
        queue_ids = queue.Queue()
        [queue_ids.put(account_id) for account_id in queue_fails.get()]
    logging.info("All reports have been obtained.")
    merge_output(output, temporal_path)
    shutil.rmtree(temporal_path)


def run_app(token, query, query_file, output, threads, verbose):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    if verbose:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        root_logger.addHandler(stream_handler)
    # Set file handler
    with open('run.log', 'w'):
        pass
    file_handler = logging.FileHandler(filename='run.log')
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter((
        '%(asctime)s.%(msecs)03d\t%(threadName)s'
        '\t%(module)s.%(funcName)s\t%(levelname)s\t%(message)s'
    ), datefmt='%Y-%m-%d %H:%M:%S'))
    root_logger.addHandler(file_handler)
    # Build AWQL report
    if query is None:
        logging.info("Loading AWQL query from file.")
        query = read_query(query_file)
    if query:
        get_report(token, query, output, threads)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="PyAwReporting",
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50)
    )
    required_arguments = parser.add_argument_group('required arguments')
    query_group = required_arguments.add_mutually_exclusive_group(required=True)
    query_group.add_argument('-a', '--awql', help="pass AWQL query", type=str)
    query_group.add_argument('-q', '--query-file', help="...or use a query file", type=str)
    parser.add_argument('-t', '--token', help="specify AdWords YAML token path", default=None)
    parser.add_argument('-o', '--output', help="define output file name", default='report.csv')
    parser.add_argument('-n', '--num-thread', help="set number of threads", type=int, default=10)
    parser.add_argument('-v', '--verbose', help="display activity", action='store_true')
    args = parser.parse_args()
    run_app(args.token, args.awql, args.query_file, args.output, args.num_thread, args.verbose)
