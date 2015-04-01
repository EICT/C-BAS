#!/usr/bin/env python

import json
import logging
import federationauthority
import connection
import report
import optparse


class Tests():

    authorities = []
    definitions = []
    success = 0
    fail = 0
    fail_details = []

    def __init__(self, options):
        definitions_file = open('definitions.json')
        self.definitions = json.load(definitions_file)
        self.options = options
        config_file = open('config.json')
        self.config = json.load(config_file)
        self._add_authorities()

    def _add_authorities(self):
        for name, authority in self.config.iteritems():
            auth = federationauthority.Authority(name, authority,
                                                 self.definitions, self)
            self.authorities.append(auth)

    def run(self):
        for authority in self.authorities:
            authority.test()

    def report(self):
        report.Report(self)

    def _credential_list(self, path):
        """Returns the _user_ credential for the given user_name."""
        return [{"SFA": self._get_file_contents(path)}]

    def _get_file_contents(self, path):
        contents = None
        with open(path, 'r') as f:
            contents = f.read()
        return contents

    def _get_paths(self, user):
        key_path = self.options.creds + '%s-key.pem' % (user, )
        cert_path = self.options.creds + '%s-cert.pem' % (user, )
        cred_path = self.options.creds + '%s-cred.xml' % (user, )
        return (key_path, cert_path, cred_path)

    def make_calls(self, calls, outcome,
                   create=False,
                   lookup=False,
                   cleanup=False,
                   user=None):
        if not user:
            user = self.options.admin
        results = []
        key_path, cert_path, cred_path = self._get_paths(user)
        cert = self._get_file_contents(cert_path)
        for call in calls:
            if 'urn' in call.keys():
                params = [call['type'].upper(), call['urn'], cert,
                          self._credential_list(cred_path),
                          {'fields': call['options']}]
            else:
                params = [call['type'].upper(), cert,
                          self._credential_list(cred_path),
                          {'fields': call['options']}]
            code, value, reason = connection.api_call(call['method'],
                                                      call['endpoint'],
                                                      params=params,
                                                      key_path=key_path,
                                                      cert_path=cert_path)
            result = {'code': code, 'value': value, 'reason': reason}
            results.append(result)
            if 'code' in outcome.keys():
                if not outcome['code'] == None:
                    try:
                        assert outcome['code'] == result['code']
                        logging.debug('Code matches')
                        self.success += 1
                    except AssertionError:
                        logging.error('Codes do not match!')
                        self.fail += 1
                        self.fail_details.append({
                            'expected_code': outcome['code'],
                            'actual_code': code,
                            'value': value,
                            'reason': reason,
                            'call': call
                        })
            if cleanup:
                try:
                    code, value, reason = connection.api_call(
                        'delete', call['endpoint'],
                        params=params,
                        key_path=key_path,
                        cert_path=cert_path)
                except:
                    pass
        return results


def parse_options():
    parser = optparse.OptionParser()
    parser.add_option('-v', '--verbosity',
                      action="store",
                      dest='verbosity',
                      type="int",
                      default=20)
    parser.add_option('-l', '--log',
                      action="store",
                      dest='log',
                      default='report.csv')
    parser.add_option('-a', '--admin',
                      action="store",
                      dest='admin',
                      default='root')
    parser.add_option('-u', '--user',
                      action="store",
                      dest='user',
                      default='alice')
    parser.add_option('-i', '--invalid',
                      action="store",
                      dest='invalid',
                      default='malcom')
    parser.add_option('-c', '--creds',
                      action="store",
                      dest='creds',
                      default='creds/')
    options, _ = parser.parse_args()
    return options


if __name__ == '__main__':
    options = parse_options()
    logging.basicConfig(level=options.verbosity)
    tests = Tests(options)
    tests.run()
    tests.report()
