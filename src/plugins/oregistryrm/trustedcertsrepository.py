import sys
import os.path
import xmlrpclib
import eisoil.core.pluginmanager as pm
from eisoil.config import  expand_eisoil_path
import threading
import time
import eisoil.core.log
logger=eisoil.core.log.getLogger('oregistryrm')

__author__ = 'umar.toseef'

class SynchRootCerts(object):

    """
    Periodically pulls trusted root certificates from peers mentioned in config file

    Generates neccessary fields when creating a new object.
    """
    CH_CERT_FILE = 'ch-cert.pem'
    CH_KEY_FILE = 'ch-key.pem'
    PULL_REQUEST_INTERVAL_SEC = 60*60*1
    SELF_WARMUP_TIME_SEC = 10

    def __init__(self):
        """
        Get plugins for use in other class methods.

        """
        super(SynchRootCerts, self).__init__()
        config = pm.getService("config")
        self._trusted_cert_path = expand_eisoil_path(config.get("delegatetools.trusted_cert_path"))
        self._ch_cert_file = os.path.join(self._trusted_cert_path, SynchRootCerts.CH_CERT_FILE)
        self._ch_cert_key_file = os.path.join(expand_eisoil_path(config.get("delegatetools.trusted_cert_keys_path")),
                                              SynchRootCerts.CH_KEY_FILE)
        self._delegate_tools = pm.getService('delegatetools')
        self._trusted_peers = self._delegate_tools.get_registry()["TRUSTED_PEERS"]

        # No need to run daemon thread if there are no federating islands
        if len(self._trusted_peers) == 0 or (len(self._trusted_peers) == 1 and self._trusted_peers[0]['host_ip'] == '0.0.0.0'):
            logger.info('No valid entries for trusted peers. Daemon thread for synchronizing trusted certs will not start.')
            return

        # To avoid running daemon thread before reloader
        e = os.environ.get('RELOADED', '0')
        if e is '0':
            os.environ['RELOADED'] = '1'
            return

        # Create a daemon thread and start it
        th = threading.Thread(target=self.synch_certs)
        th.daemon = True
        th.start()
        logger.info('Daemon thread for synchronizing trusted certs started.')

    def synch_certs(self):
        """
        Runs forever in order to synchronize root certs with trusted peer
        """

        time.sleep(SynchRootCerts.SELF_WARMUP_TIME_SEC)
        self_authority = self.get_self_authority()
        geniutil = pm.getService('geniutil')
        while True:

            for peer in self._trusted_peers:
                cert_list = self.pull_certs(peer['host_endpoint'], peer['host_ip'], peer['host_port'])
                if cert_list:
                    for cert in cert_list:
                        info = geniutil.extract_certificate_info(cert)
                        if info:
                            auth, typ, name = geniutil.decode_urn(info[0])
                            if (not auth == self_authority) and name in ['ca', 'sa', 'ma']:
                                file_name = "+".join([auth, typ, name])+'-cert.pem'
                                file_path = os.path.join(self._trusted_cert_path, file_name)
                                if not os.path.isfile(file_path):
                                    with open(file_path,"w") as f:
                                        f.write(cert)
                                    logger.info("Wrote pulled cert file %s from %s", file_name, peer['host_ip'])
            time.sleep(SynchRootCerts.PULL_REQUEST_INTERVAL_SEC)

    def pull_certs(self, endpoint="reg/2", host='0.0.0.0', port=8008):

        # Do nothing if valid IP address has not been provided
        if host == '0.0.0.0':
            return
        transport = SafeTransportWithCert(self._ch_cert_key_file, self._ch_cert_file)
        proxy = xmlrpclib.ServerProxy("https://%s:%s/%s" % (host, str(port), endpoint), transport=transport)
        method = getattr(proxy, "get_trust_roots")
        params = []

        try:
            return_values = method(*params)
            if return_values['code'] == 0:
                return return_values['value']

            else:
                logger.error('failed to pull trusted cert from %s', host)
        except:
                logger.error('failed to pull trusted cert from %s', host)

    def get_self_authority(self):

        with open(self._ch_cert_file, 'r') as f:
            cert = f.read()
        geniutil = pm.getService('geniutil')
        info = geniutil.extract_certificate_info(cert)
        if info:
            auth,_,_  = geniutil.decode_urn(info[0])
            return auth
        else:
            logger.error('Failed to get self authority')


class SafeTransportWithCert(xmlrpclib.SafeTransport):
    """Helper class to force the right certificate for the transport class."""
    def __init__(self, key_path, cert_path):

        if sys.version_info >= (2,7,9):
            import ssl
            xmlrpclib.SafeTransport.__init__(self, context=ssl._create_unverified_context())
        else:
            xmlrpclib.SafeTransport.__init__(self) # no super, because old style class
        self._key_path = key_path
        self._cert_path = cert_path

    def make_connection(self, host):
        """This method will automatically be called by the ServerProxy class when a transport channel is needed."""
        host_with_cert = (host, {'key_file' : self._key_path, 'cert_file' : self._cert_path})
        return xmlrpclib.SafeTransport.make_connection(self, host_with_cert) # no super, because old style class