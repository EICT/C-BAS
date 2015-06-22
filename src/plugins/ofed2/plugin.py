import eisoil.core.pluginmanager as pm
from oregistryvtwodelegate import ORegistryv2Delegate
from osavtwodelegate import OSAv2Delegate
from omavtwodelegate import OMAv2Delegate
from ologgingdelegate import OLoggingDelegate

"""
The delegate concept (introduced by eiSoil) was extended here.
Now there is the delegate which does the actual work (either itself or delegates to a Resource Manager).
The delegate may be wrapped in a guard.
This guard derives from the original delegate and checks the incoming/outgoing values with respect to authorization.
E.g. The orginal delegate would deliver private information to the user becuase it is not concerned with authorization.
The guard on the other hand checks the outgoing result and raises an exception if the user does not have the right privileges.
"""
def setup():
    config = pm.getService('config')
    config.install("ofed.cert_root", "deploy/trusted", "Folder which includes trusted certificates (in .pem format). If relative path, the root is assumed to be git repo root.")

    reg_delegate = ORegistryv2Delegate()
    reg_handler = pm.getService('gregistryv2handler')
    reg_handler.setDelegate(reg_delegate)

    ma_delegate = OMAv2Delegate()
    ma_handler = pm.getService('gmav2handler')
    ma_handler.setDelegate(ma_delegate)

    sa_delegate = OSAv2Delegate()
    sa_handler = pm.getService('gsav2handler')
    sa_handler.setDelegate(sa_delegate)

    log_delegate = OLoggingDelegate()
    log_handler = pm.getService('glogginghandler')
    log_handler.setDelegate(log_delegate)
