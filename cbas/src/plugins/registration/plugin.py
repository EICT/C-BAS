from eisoil.core import pluginmanager as pm

def setup():

    import registration_server
    pm.registerService('registration', registration_server)
