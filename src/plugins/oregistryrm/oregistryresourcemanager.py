import eisoil.core.pluginmanager as pm
from eisoil.config import  expand_eisoil_path
import os
import eisoil.core.log
from trustedcertsrepository import SynchRootCerts
logger=eisoil.core.log.getLogger('oregistryrm')


from oregistryexceptions import *

class ORegistryResourceManager(object):
    """
    Manage Federation Registry objects and resources.
    """

    AGGREGATE_SERVICE_TYPE = 'AGGREGATE_MANAGER' #: Field name used to denote an Aggregate Manager in the configuration (config.json)
    SA_SERVICE_TYPE = 'SLICE_AUTHORITY' #: Field name used to denote a Slice Authority in the configuration (config.json)
    MA_SERVICE_TYPE = 'MEMBER_AUTHORITY' #: Field name used to denote a Member Authority in the configuration (config.json)

    TYPES =  [AGGREGATE_SERVICE_TYPE, SA_SERVICE_TYPE, MA_SERVICE_TYPE] #: Combined list of all service types found in the configuration (config.json)

    AUTHORITY_NAME = 'fr' #: The short-name for this authority

    SUPPORTED_SERVICES = ['SERVICE'] #: The objects supported by this authority

    def __init__(self):
        """
        Get plugins for use in other class methods.
        """
        super(ORegistryResourceManager, self).__init__()
        self._resource_manager_tools = pm.getService('resourcemanagertools')
        # TODO: this isn't a delegate!
        self._delegate_tools = pm.getService('delegatetools')

        # Initialize SynchRootCerts
        synch = SynchRootCerts()

    def urn(self):
        """
        Get the URN for this Federation Registry.

        Retrieve the hostname from the Flask eiSoil plugin and use this to build
        the URN.

        """
        oma = pm.getService('omemberauthorityrm')
        return 'urn:publicid:IDN+' + oma._hostname + '+authority+fr'

    def implementation(self):
        """
        Get the implementation details for this Federation Registry.

        Retrieve details from the eiSoil plugin and form them into a dictionary
        suitable for the API call response.

        """
        manifest = pm.getManifest('oregistryrm')
        if len(manifest) > 0:
            return {'code_version' : str(manifest['version'])}
        else:
            return None

    def services(self):
        """
        Return the services implemented by this Federation Registry.
        """
        return self.SUPPORTED_SERVICES

    def service_types(self):
        """
        Return the service types, as defined in the registry config file (registry.json).
        """
        service_types = set()
        for e in self._delegate_tools.get_registry()['SERVICES']:
            service_types.add(e['service_type'])
        return list(service_types)

    def lookup_services(self):
        """
        Return all service types as defined in the  registry config file (registry.json).
        """
        # return self._uppercase_keys_in_list([e for e in self._delegate_tools.get_registry()["SERVICES"] if (e['service_type'] in self.TYPES)])
        # Current deployments assume single SA and MA authorities

        services = []
        for e in self._delegate_tools.get_registry()["SERVICES"]:

            if e['service_type'] in [self.SA_SERVICE_TYPE, self.MA_SERVICE_TYPE]:
                rm = pm.getService('osliceauthorityrm') if e['service_type'] == self.SA_SERVICE_TYPE else pm.getService('omemberauthorityrm')

                endpoints = pm.getService('apitools').get_endpoints(type=rm.AUTHORITY_NAME)
                if endpoints:
                    e['service_url'] = "https://"+pm.getService('gregistryv2handler').bindAddress()+endpoints[0]['url']

                e['service_urn'] = rm.urn()
                e['service_cert'] = '<certificate>'+rm.authority_certificate()+'</certificate>'

            services.append(e)

        return self._uppercase_keys_in_list(services)

    def all_aggregates(self):
        """
        Return all aggregates as defined in the registry config file (registry.json).
        """
        return self._uppercase_keys_in_list([e for e in self._delegate_tools.get_registry()["SERVICES"] if (e['service_type']==self.AGGREGATE_SERVICE_TYPE)])

    def all_member_authorities(self):
        """
        Return all member authorities as defined in the registry config file (registry.json).
        """
        return self._uppercase_keys_in_list([e for e in self._delegate_tools.get_registry()["SERVICES"] if (e['service_type']==self.MA_SERVICE_TYPE)])

    def all_slice_authorities(self):
        """
        Return all slice authorities as defined in the registry config file (registry.json).
        """
        # return self._uppercase_keys_in_list([e for e in self._delegate_tools.get_registry()["SERVICES"] if (e['service_type']==self.SA_SERVICE_TYPE)])
        # Current deployments assume single slice authority


    def all_trusted_certs(self):
        """
        Return all trusted certificates as defined in the registry config file (registry.json).
        """
        certs = self._delegate_tools.get_registry()["TRUST_ROOTS"]
        #TODO: Subsitute magic markers
        if "INFER_SAs" in certs:
            certs.remove("INFER_SAs")
            for s in self.all_slice_authorities():
                certs.append(s['SERVICE_CERT'])
        if "INFER_MAs" in certs:
            certs.remove("INFER_MAs")
            for s in self.all_member_authorities():
                certs.append(s['SERVICE_CERT'])

        config = pm.getService('config')
        trusted_cert_path = expand_eisoil_path(config.get("delegatetools.trusted_cert_path"))

        # Go through the dir and fetch trusted certificates
        src_files = os.listdir(trusted_cert_path)
        for file_name in src_files:
            full_file_name = os.path.join(trusted_cert_path, file_name)
            if os.path.isfile(full_file_name):
                with open (full_file_name, "r") as cert_file:
                    cert_str =cert_file.read()
                certs.append(cert_str)

        return certs

    def get_authory_mappings(self, urns):
        """
        Get authority mappings for a set of URNs.
        """
        geniutil = pm.getService('geniutil')
        if not isinstance(urns, list):
            raise ValueError("Please give a _list_ of URNs")
        result = {}
        for urn in urns:
            authority, typ, name = geniutil.decode_urn(urn)
            service = None
            if (typ == "slice"):
                service = self._find_service(self.SA_SERVICE_TYPE, authority)
            if (typ == "user"):
                service = self._find_service(self.MA_SERVICE_TYPE, authority)
            if (typ == "sliver"):
                service = self._find_service(self.AGGREGATE_SERVICE_TYPE, authority)
            if service:
                result[urn] = service['service_url']
        return result

    def _find_service(self, typ, authority):
        """
        Returns the first service dictionary matching the {typ}e and {urn}. None if none is found.
        """
        geniutil = pm.getService('geniutil')
        for service in self._delegate_tools.get_registry()['SERVICES']:
            sauth, styp, sname = geniutil.decode_urn(service['service_urn'])
            if (service['service_type'] == typ) and (sauth == authority):
                return service
        return None

    def _uppercase_keys_in_list(self, list_of_dicts):
        """
        Convert key names in a list to uppercase.
        """
        return [self._uppercase_keys_in_dict(e) for e in list_of_dicts]

    def _uppercase_keys_in_dict(self, adict):
        """
        Convert key names in a dictionary to uppercase.
        """
        return dict( (k.upper(), v) for (k, v) in adict.iteritems() )

    def _check_raise(self, condition, message):
        """
        Check if condition is true, else raises an exception with given string.
        """
        if not condition:
            raise RegistryMalformedConfigFile(oregistryutil.config_path(), message)
