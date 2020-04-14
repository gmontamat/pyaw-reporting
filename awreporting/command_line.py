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
command_line.py
Entry point for awreporting.
"""

import argparse
import logging

from awreporting.awreporting import read_query, get_report


def run_app(token, query, query_file, output, threads, verbose):
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    if verbose:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        root_logger.addHandler(stream_handler)
    # Set file handler
    with open('awreporting.log', 'w'):
        pass
    file_handler = logging.FileHandler(filename='awreporting.log')
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


def main():
    parser = argparse.ArgumentParser(
        description="AwReporting - Large scale AdWords reporting tool in Python",
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
