import eisoil.core.pluginmanager as pm
import eisoil.core.log

logger=eisoil.core.log.getLogger('ologgingauthorityrm')

from ologgingauthorityexceptions import *
from eisoil.config import  expand_eisoil_path
from apiexceptionsv2 import *
import datetime as dt
import time

class OLoggingAuthorityResourceManager(object):
    """
    Manage Logging Authority objects

    Generates necessary fields when creating a new object.
    """
    AUTHORITY_NAME = 'ls'  #: The short-name for this authority

    SUPPORTED_SERVICES = ['Logging', 'Accounting']  #: The objects supported by this authority

    SUPPORTED_CREDENTIAL_TYPES = [{"type": "SFA", "version": 1}]  #: The credential type supported by this authority

    def __init__(self):
        """
        Get plugins for use in other class methods.

        Set unique keys.
        """
        super(OLoggingAuthorityResourceManager, self).__init__()
        self._resource_manager_tools = pm.getService('resourcemanagertools')
        self._set_unique_keys()
        # self._urn = self.urn()

    def _set_unique_keys(self):
        """
        Set the required unique keys in the database.
        """
        self._resource_manager_tools.set_index(self.AUTHORITY_NAME, 'TIMESTAMP')

    # --- 'get_version' methods
    # def urn(self):
    #     """
    #     Get the URN for this Authority.
    #
    #     Retrieve the hostname from the Flask eiSoil plugin and use this to build
    #     the URN.
    #
    #     """
    #     config = pm.getService('config')
    #     hostname = config.get('flask.cbas_hostname')
    #     return 'urn:publicid:IDN+' + hostname + '+authority+ls'

    def implementation(self):
        """
        Get the implementation details for this Authority.

        Retrieve details from the eiSoil plugin and form them into a dictionary
        suitable for the API call response.

        """
        manifest = pm.getManifest('ologgingauthorityrm')
        if len(manifest) > 0:
            return {'code_version': str(manifest['version'])}
        else:
            return None

    def services(self):
        """
        Return the services implemented by this Authority.
        """
        return self.SUPPORTED_SERVICES

    def credential_types(self):
        """
        Return the credential types implemented by this Member Authority.
        """
        return self.SUPPORTED_CREDENTIAL_TYPES

    # --- object methods
    def append_event_log(self, authority, method, fields, options, target_type, actor_urn=None, target_urn=None,
                         certificate=None, credentials=None):
        """
        Append an event to log
        """

        geniutil = pm.getService('geniutil')

        # Regarding URNs following sequence is enforced: 1) actor_urn, target_urn from argument,
        # 2) actor_urn from certificate, 3a) actor_urn from credential 3b) target_urn from credentials

        if not actor_urn and certificate:
            actor_urn, _, _ = geniutil.extract_certificate_info(certificate)

        if credentials:
            _actor_urn, _target_urn = geniutil.get_owner_and_target_urn(credentials)
            if not actor_urn:
                actor_urn = _actor_urn
            if not target_urn:
                target_urn = _target_urn

        # timestamp = dt.datetime.utcnow().strftime('%Y%m%d%H%M%SZ')  # GMT time in UTC format
        timestamp = time.time()  # GMT time in UTC format

        entry = dict(TIMESTAMP=timestamp,
                     ACTOR=actor_urn,
                     TARGET=target_urn,
                     AUTHORITY=authority,
                     METHOD=method,
                     OPTIONS=options,
                     FIELDS=fields)

        return self._resource_manager_tools.object_create(self.AUTHORITY_NAME, entry, target_type)

    def lookup(self, target_type, match, filters):
        """
        Search database for desired event
        """
        if not target_type == 'ALL':
            return self._resource_manager_tools.object_lookup(self.AUTHORITY_NAME, target_type.upper(), match, filters)
        else:
            collective_results = []
            for typ in ['SLICE', 'PROJECT', 'SLIVER_INFO', 'KEY', 'MEMBER']:
                results = self._resource_manager_tools.object_lookup(self.AUTHORITY_NAME, typ, match, filters)
                if results:
                    collective_results = collective_results + results
            return collective_results
