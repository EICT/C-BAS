import eisoil.core.pluginmanager as pm
import ologgingauthorityexceptions

from ologgingauthorityresourcemanager import OLoggingAuthorityResourceManager

def setup():
    ls_rm = OLoggingAuthorityResourceManager()
    pm.registerService('ologgingauthorityrm', ls_rm)
    pm.registerService('ologgingauthorityexceptions', ologgingauthorityexceptions)