import eisoil.core.pluginmanager as pm
from eisoil.core import serviceinterface

import eisoil.core.log
logger=eisoil.core.log.getLogger('gloggingrpc')

xmlrpc = pm.getService('xmlrpc')

class GLoggingHandler(xmlrpc.Dispatcher):
    """
    Handle XML-RPC API calls for logging
    """

    def __init__(self):
        """
        Initialise logger and clear delegate.
        """
        super(GLoggingHandler, self).__init__(logger)
        self._api_tools = pm.getService('apitools')
        self._delegate = None

    @serviceinterface
    def setDelegate(self, adelegate):
        """
        Set this object's delegate.
        """
        self._delegate = adelegate

    @serviceinterface
    def getDelegate(self):
        """
        Get this object's delegate.
        """
        return self._delegate


    def lookup(self, target_type, options):
        """
        Lookup objects with given type.

        Unwrap 'match' and 'filter' fields out of 'options'.

        Ignore credentials, as this is an unprotected call.

        Call delegate method and return result or exception.

        """
        try:
            match, filter_ = self._api_tools.fetch_match_and_filter(options)
            result = self._delegate.lookup(target_type, match, filter_)
        except Exception as e:
            return self._api_tools.form_error_return(logger, e)
        return self._api_tools.form_success_return(result)


class GLoggingDelegateBase(object):
    """
    The contract of this class (methods, params and returns) are derived from the GENI Federation MA API (v2).
    """

    def __init__(self):
        super(GMAv2DelegateBase, self).__init__()

    # ---- General methods
    def get_version(self):
        """
        Return information about version and options
          (e.g. filter, query, credential types) accepted by this service

        Arguments: None

        Return:
            get_version structure information as described above
        """
        raise GFedv2NotImplementedError("Method not implemented")

    def lookup(self, type_, credentials, options):
        """
        Lookup requested details for objects matching 'match' options.
        This call takes a set of 'match' criteria provided in the 'options' field,
        and returns a dictionary of dictionaries of object attributes
        keyed by object URN matching these criteria.
        If a 'filter' option is provided, only those attributes listed in the 'filter'
        options are returned.
        The requirements on match criteria supported by a given service
        are service-specific; however it is recommended that policies
        restrict lookup calls to requests that are bounded
        to particular sets of explicitly listed objects (and not open-ended queries).

        See additional details on the lookup method in the document section below.


        Arguments:
           type: type of objects for which details are being requested
           options: What details to provide (filter options)
                   for which objects (match options)

        Return: List of dictionaries (indexed by object URN) with field/value pairs
          for each returned object
        """
        raise GFedv2NotImplementedError("Method not implemented")
