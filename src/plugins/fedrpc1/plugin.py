import eisoil.core.pluginmanager as pm
from fedrpcone.gregistryvone import GRegistryv1Handler, GRegistryv1DelegateBase
from fedrpcone.gmavone import GMAv1Handler, GMAv1DelegateBase
from fedrpcone.gsavone import GSAv1Handler, GSAv1DelegateBase
from fedrpcone import exceptions as gfed_exceptions

def setup():
    pm.registerService('gfedv1exceptions', gfed_exceptions)

    xmlrpc = pm.getService('xmlrpc')
    _api_tools = pm.getService('apitools')

    greg_handler = GRegistryv1Handler()
    pm.registerService('gregistryv1handler', greg_handler)
    pm.registerService('gregistryv1delegatebase', GRegistryv1DelegateBase)
    xmlrpc.registerXMLRPC('greg', greg_handler, '/reg/1') # name, handlerObj, endpoint
    # _api_tools.register_endpoint(name='gregv1', type='reg', version='1', url='/reg/1')

    gma_handler = GMAv1Handler()
    pm.registerService('gmav1handler', gma_handler)
    pm.registerService('gmav1delegatebase', GMAv1DelegateBase)
    xmlrpc.registerXMLRPC('gma', gma_handler, '/ma/1') # name, handlerObj, endpoint
    # _api_tools.register_endpoint(name='gmav1', type='ma', version='1', url='/ma/1')

    gsa_handler = GSAv1Handler()
    pm.registerService('gsav1handler', gsa_handler)
    pm.registerService('gsav1delegatebase', GSAv1DelegateBase)
    xmlrpc.registerXMLRPC('gsav1', gsa_handler, '/sa/1') # name, handlerObj, endpoint
    # _api_tools.register_endpoint(name='gsav1', type='sa', version='1', url='/sa/1')
