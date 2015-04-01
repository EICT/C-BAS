#!/usr/bin/env python

import sys
import csv


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Report:
    def __init__(self, tests):
        self.tests = tests
        self._print_results(path=tests.options.log)
        self._generate_exit_code()

    def _print_results(self, path='report.csv'):
        print bcolors.OKGREEN + 'Successful tests: ' + str(self.tests.success)
        print bcolors.FAIL + 'Failed tests: ' + str(self.tests.fail)
        if self.tests.fail > 0:
            print bcolors.WARNING + 'For more details and a full log of test failures, please see "' + str(
                path) + '"'
            self._generate_log_file(path)
        else:
            print bcolors.OKBLUE + 'All tests passed successfully!'

    def _generate_log_file(self, path='report.csv'):
        with open(path, 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Expected Code', 'Actual Code', 'Method Call',
                             'Reason', 'Value'])
            for fail in self.tests.fail_details:
                writer.writerow([fail['expected_code'], fail['actual_code'],
                                 fail['call'], fail['reason'], fail['value']])

    def _generate_exit_code(self):
        if self.tests.fail > 0:
            sys.exit(1)
        else:
            sys.exit(0)
