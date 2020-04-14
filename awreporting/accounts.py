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
accounts.py
Retrieves account information using the AdWords API
ManagedCustomerService.
"""

import logging
import sys

from googleads import adwords


def get_managed_customer_data(adwords_client, selector, max_retries=10):
    # Initialize API ManagedCustomerService
    ctr = 0
    while True:
        try:
            managed_customer_service = adwords_client.GetService(
                'ManagedCustomerService', version='v201809'
            )
            break
        except Exception as e:
            logging.exception("Couldn't initialize ManagedCustomerService.")
            ctr += 1
            if ctr == max_retries:
                logging.warning("No accounts were retrieved.")
                return []
    # Get serviced account graph
    ctr = 0
    while True:
        try:
            graph = managed_customer_service.get(selector)
            break
        except Exception as e:
            logging.exception("Couldn't retrieve account graph.")
            ctr += 1
            if ctr == max_retries:
                logging.warning("No accounts were retrieved.")
                return []
    if 'entries' in graph and graph['entries']:
        return graph['entries']
    logging.warning("No accounts were found.")
    return []


def get_account_ids(token, account_id=None):
    try:
        adwords_client = adwords.AdWordsClient.LoadFromStorage(token)
    except Exception as e:
        logging.exception("Couldn't initialize AdWordsClient.")
        sys.exit(1)
    # If passed, set account id
    if account_id:
        adwords_client.SetClientCustomerId(account_id)
    # Construct selector to get all valid account ids
    selector = {
        'fields': ['CustomerId'],
        'predicates': [{
            'field': 'CanManageClients',
            'operator': 'EQUALS',
            'values': ['false']
        }]
    }
    accounts = get_managed_customer_data(adwords_client, selector)
    account_ids = []
    for account in accounts:
        account_ids.append(account['customerId'])
    return account_ids


if __name__ == '__main__':
    print(get_account_ids('example.yaml'))
