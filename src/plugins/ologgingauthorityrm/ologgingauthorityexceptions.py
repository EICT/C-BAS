from eisoil.core.exception import CoreException
        
class OLoggingAuthorityException(CoreException):
    def __init__(self, desc):
        self._desc = desc
    def __str__(self):
        return "OLoggingAuthority: %s" % (self._desc,)
