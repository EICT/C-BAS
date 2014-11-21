import amsoil.core.pluginmanager as pm
from resourcemanagertools import ResourceManagerTools
from delegatetools import DelegateTools
from apitools import APITools
import apiexceptionsv1, apiexceptionsv2

def setup():

    pm.registerService('apiexceptionsv1', apiexceptionsv1)
    pm.registerService('apiexceptionsv2', apiexceptionsv2)

    api_tools = APITools()
    pm.registerService('apitools', api_tools)

    resource_manager_tools = ResourceManagerTools()
    pm.registerService('resourcemanagertools', resource_manager_tools)

    config = pm.getService("config")
    config.install("delegatetools.config_path", "deploy/config.json", "JSON file with configuration data for CH, SA, MA")
    config.install("delegatetools.supplemetary_fileds_path", "deploy/supplementary_fields.json", "JSON file with Supplementary Fields for CH, SA, MA",True)
    config.install("delegatetools.service_registry_path","deploy/registry.json", "JSON file with Services supported by the registry",True)
    config.install("delegatetools.defaults_path", "src/plugins/fedtools/defaults.json", "JSON file with default data for CH, SA, MA", True)
    #<UT>
    config.install("delegatetools.authz_path", "src/plugins/fedtools/authz.json", "JSON file with mapping between privileges and methods", True)
    config.install("delegatetools.roles_path", "src/plugins/fedtools/roles.json", "JSON file with default privileges for CH roles", True)
    config.install("delegatetools.trusted_cert_path", "deploy/trusted/certs/", "Path to trusted certificates", True)
    config.install("delegatetools.trusted_cert_keys_path", "deploy/trusted/cert_keys", "Path to trusted certificate keys", True)
    config.install("delegatetools.trusted_crl_path", "deploy/trusted/crl", "Path to CRLs", True)

    delegate_tools = DelegateTools()
    pm.registerService('delegatetools', delegate_tools)

