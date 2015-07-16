import eisoil.core.pluginmanager as pm
import eisoil.core.log
logger=eisoil.core.log.getLogger('ofed')

gfed_ex = pm.getService('apiexceptionsv2')
GLoggingDelegateBase = pm.getService('gloggingdelegatebase')

class OLoggingDelegate(GLoggingDelegateBase):
    """
    Implements Federation Registry methods.
    """

    def __init__(self):
        """
        Get plugins for use in other class methods.

        Checks consistency of 'SERVICES' fields defined in configuration
        (config.json).
        """
        self._logging_authority_resource_manager = pm.getService('ologgingauthorityrm')


    def lookup(self, target_type, match, filters):
        """
        Depending on the object type defined in the request, lookup this object
        using the resource manager.
        """
        if target_type:
            return self._logging_authority_resource_manager.lookup(target_type.upper(), match, [] if filters is None else filters)
        else:
            raise gfed_ex.GFedv2ArgumentError("Target type should be one of the followings: slice, project, member, key, sliver_info, all" )