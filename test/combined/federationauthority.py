#!/usr/bin/env python

import logging
import federationobject


class IterMixin(object):
    def __iter__(self):
        for attr, value in self.__dict__.iteritems():
            yield attr, value


class Authority(IterMixin):
    def __init__(self, name, authority, definitions, tests):
        self.__dict__ = authority
        self.logger = logging.getLogger(name)
        self.objs = []
        self.name = name

        self.logger.debug(name+' Federation authority created')
        for object_ in self.supported_object_types:
            if "object" in object_:
                name = object_["object"].lower()
                obj = federationobject.Obj(name, object_, definitions[name],
                                           self.endpoint, tests)
                self.objs.append(obj)

    def test(self):
        for key in dict(self).iterkeys():
            getattr(self, 'test_' + key)()

    def test_methods(self):
        for method in self.methods:
            getattr(self, 'test_method_' + method)()

    def test_supported_object_types(self):
        for obj in self.objs:
            obj.test()

    def test_objs(self):
        pass

    def test_name(self):
        pass

    def test_logger(self):
        pass

    def test_endpoint(self):
        pass

    def test_method_get_version(self):
        self.logger.info('Testing "get_version" method')

    def test_method_get_credentials(self):
        self.logger.info('Testing "get_credentials" method')

    def test_method_modify_membership(self):
        self.logger.info('Testing "modify_membership" method')

    def test_method_lookup_members(self):
        self.logger.info('Testing "lookup_members" method')

    def test_method_lookup_for_member(self):
        self.logger.info('Testing "lookup_for_member" method')

    def test_method_get_trust_roots(self):
        self.logger.info('Testing "get_trust_roots" method')

    def test_method_lookup_authorities_for_urns(self):
        self.logger.info('Testing "lookup_authorities_for_urns" method')
