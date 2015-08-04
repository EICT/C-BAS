#!/usr/bin/env python

import generator
import logging
import copy

method_mapping = {
    'create': ['creation'],
    'update': ['update'],
    'delete': [],
    'lookup': ['match', 'protection']
}
true_values = ['yes', True, 'required', 'public']
permissive_true_values = ['allowed']
false_values = ['no', False]
permissive_false_values = ['not allowed']  # depends on AuthZ policy


class Obj():
    def __init__(self, name, obj, definition, endpoint, tests):
        global method_mapping
        self.__dict__ = obj
        self.__dict__.update(definition)
        self.name = name
        self.tests = tests
        self.endpoint = endpoint
        self.logger = logging.getLogger(name)
        self._amalgamate_permissive_values()
        self.logger.debug('Federation object created')

    def _amalgamate_permissive_values(self):
        self.permissive_true_values = permissive_true_values + true_values
        self.permissive_false_values = permissive_false_values + false_values

    def test(self):
        self.logger.info('Testing federation object')
        self._test_allowed()
        self._test_duplicate()
        self._test_credential_validity()
        self._test_type_validation()
        for method in method_mapping.keys():
            if method in self.methods:
                getattr(self, 'test_' + method)()
        if not self.name == 'service':
            for method in method_mapping.keys():
                if method not in self.methods:
                    self._test_not_implemented(method)

    def test_logger(self):
        pass

    def test_name(self):
        pass

    def test_enpoint(self):
        pass

    def test_create(self):
        self.logger.info('Testing "create" method')
        if not self.name == 'service':
            self._check_true_and_false('create', cleanup=True)

    def test_update(self):
        self.logger.info('Testing "update" method')
        # self._check_true_and_false('update', urn=generator.generate('urn'))

    def test_delete(self):
        self.logger.info('Testing "delete" method')
        if not self.name == 'service':
            self._check_true_and_false('delete', urn=generator.generate('urn'))

    def test_lookup(self):
        self.logger.info('Testing "lookup" method')
        self._check_true_and_false('lookup')

    def _create_options(self, method, truth_values, urn=None):
        options = {}
        for field in self.request_template:
            for test in method_mapping[method]:
                try:
                    if field[test] in truth_values:
                        if urn and self.name in ['key', 'member'] and field['name'] in ['KEY_MEMBER', 'MEMBER_URN']:
                            options[field['name']] = urn
                        else:
                            options[field['name']] = generator.generate(field['type'])
                except KeyError:
                    pass
        return options

    def _create_duplicate_options(self, method, truth_values, invalid=False):
        options = self._create_options(method, true_values)
        testing = []
        for field in self.request_template:
            for test in method_mapping[method]:
                try:
                    if field[test] in truth_values:
                        options_dup = copy.copy(options)
                        options_dup[field['name']] = generator.generate(
                            field['type'],
                            invalid=invalid)
                        if 'SLICE_NAME' in options_dup.keys(): # 1. SLICE name must be unique, 2. Created SLICE cannot be deleted
                            options_dup['SLICE_NAME'] = generator.generate('string', invalid=invalid)
                        elif 'SLIVER_INFO_URN' in options_dup.keys(): # SLIVER_INFO_URN must be unique
                            options_dup['SLIVER_INFO_URN'] = generator.generate('urn', invalid=invalid)
                        elif 'PROJECT_NAME' in options_dup.keys(): # PROJECT_NAME must be unique
                            options_dup['PROJECT_NAME'] = generator.generate('string', invalid=invalid)
                        elif 'MEMBER_USERNAME' in options_dup.keys(): # MEMBER_USERNAME must be unique
                            options_dup['MEMBER_USERNAME'] = generator.generate('username', invalid=invalid)
                        elif 'KEY_PUBLIC' in options_dup.keys(): # KEY_PUBLIC must be unique
                            options_dup['KEY_PUBLIC'] = generator.generate('key', invalid=invalid)

                        testing.append(options_dup)
                except KeyError:
                    pass
        return testing

    def _find_key(self, response, name):
        if not response:
            return None
        keys = [str(name + '_urn').upper(), str(name + '_slice_urn').upper(),
                str(self.name+'_id').upper(), str(self.name + '_member').upper()]
        for key in keys:
            if key in response.keys():
                return key

    def _test_allowed(self, user=None, code=0):
        if not user:
            user = self.tests.options.admin

        if 'create' in self.methods:
            options = self._create_options('create', self.permissive_true_values)
            call = {
                    'method': 'create',
                    'type': self.name,
                    'endpoint': self.endpoint,
                    'options': options
                }
            response = self.tests.make_calls(
                    calls=[call],
                    outcome={'result': 1,
                             'code': code},
                    user=user)[0]  #TODO: Handle multiple return values
            if 'lookup' in self.methods:
                options = self._create_options('lookup', true_values)
                call = {
                    'method': 'lookup',
                    'type': self.name,
                    'endpoint': self.endpoint,
                    'options': options
                }

                self.tests.make_calls(
                    calls=[call],
                    outcome={'result': 1,
                             'code': code},
                    user=user)
                urn_key = None
            if 'update' in self.methods:
                    urn_key = self._find_key(response['value'], self.name)
                    options = self._create_options('update',
                                                   self.permissive_true_values)
                    call['method'] = 'update'
                    call['urn'] = response['value'][urn_key]
                    call['options'] = options
                    self.tests.make_calls(calls=[call],
                                          outcome={'result': 1,
                                                   'code': code},
                                          user=user)

            if 'delete' in self.methods:
                    if urn_key is None:
                        urn_key = self._find_key(response['value'], self.name)
                    call['method'] = 'delete'
                    call['urn'] = response['value'][urn_key]
                    call['options'] = options
                    self.tests.make_calls(calls=[call],
                                          outcome={'result': 0,
                                                   'code': code},
                                          user=user)
        else:
            self.logger.info(
                'Could not test object; no way to create test data!')

    def _test_not_implemented(self, method):
        self.logger.info('Testing "NOT_IMPLEMENTED_ERROR"')
        call = {
            'method': method,
            'type': self.name,
            'endpoint': self.endpoint,
            'options': '',
        }
        if method == 'delete' or method == 'update':
            call['urn'] = ''
        try:
            self.tests.make_calls(calls=[call],
                                  outcome={'result': None,
                                           'code': 100})
        except Exception as e:
            self.logger.error(str(e)
                             )  #TODO: registry is not returning 100 errors

    def _test_duplicate(self):
        if not self.name == 'service':
            options = self._create_options('create', true_values)
            call = {
                'method': 'create',
                'type': self.name,
                'endpoint': self.endpoint,
                'options': options
            }
            self.tests.make_calls(calls=[call],
                                  outcome={'result': None,
                                           'code': 0})
            self.tests.make_calls(calls=[call],
                                  outcome={'result': None,
                                           'code': 5})

    def _test_type_validation(self):
        self._bundle_calls('create', true_values, None, 0, cleanup=True)
        self._bundle_calls('create', true_values, None, 3,
                           cleanup=True,
                           invalid=True)

    def _test_credential_validity(self):
        if not self.name == 'service':
            urn = self.tests.get_urn(self.tests.options.user)
            options = self._create_options('create', true_values, urn)
            call = {
                'method': 'create',
                'type': self.name,
                'endpoint': self.endpoint,
                'options': options
            }
            self.tests.make_calls(calls=[call],
                                  outcome={'result': None,
                                           'code': 0 if not self.name == 'member' else 2},
                                    user=self.tests.options.user, cleanup=True)
            self.tests.make_calls(calls=[call],
                                  outcome={'result': None,
                                           'code': 2},
                                    user=self.tests.options.invalid, cleanup=True) #should be 1, but SSL connection breaks first

    def _bundle_calls(self, method, truth_values, result, code,
                      create=True,
                      cleanup=True,
                      invalid=False,
                      urn=None,
                      duplicate=False):
        multi_options = self._create_duplicate_options(method, truth_values,
                                                       invalid)
        calls = []
        template = {
            'method': method,
            'endpoint': self.endpoint,
            'type': self.name
        }
        if urn:
            template['urn'] = urn
        for options in multi_options:
            template['options'] = options
            calls.append(copy.copy(template))
        self.tests.make_calls(calls=calls,
                              outcome={'result': result,
                                       'code': code},
                              lookup=method == 'lookup',
                              cleanup=cleanup)
        return str(len(multi_options))

    def _check_true_and_false(self, method, urn=None, cleanup=False):
        self._bundle_calls(method, self.permissive_true_values, None, 0, urn=urn)
        self._bundle_calls(method, self.permissive_false_values, None, 3, urn=urn)
