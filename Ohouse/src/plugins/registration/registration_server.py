import amsoil.core.pluginmanager as pm
import hashlib, datetime

from amsoil.config import  expand_amsoil_path
from amsoil.config import (registration_server_ip, registration_server_port)
from SocketServer import ThreadingMixIn
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from registration_utils import *


KEY_PATH = expand_amsoil_path('test/creds') + '/'
AUTHORITY_NAME = 'ma'

AUTHORITY="test:fp7-ofelia:eu"
MA_CERT_FILE = 'ma-cert.pem'
MA_KEY_FILE = 'ma-key.pem'

CRED_EXPIRY = datetime.datetime.utcnow() + datetime.timedelta(days=100)

class RegistrationAppServer(ThreadingMixIn, SimpleJSONRPCServer):
    pass

def register_user(first_name, last_name, user_name, user_email, public_key=None, privileges=[]):
    """
    Register user by creating public ssh Keys and credentials

    Args:
        first_name: The first name of the user which will be included in the URN
        last_name: The last name of the user which will be included in the URN
        username: A name that might be used to reference a certail user
        email : The User Email
        public_key: An optional field, allows a user-generated public key
        privileges: list of privileges to be included in user credentials

    Return:
        User generated data such as keys, credentials, etc.
    """

    #<UT> Check if proper arguments were passed
    if not (first_name and last_name and user_name and user_email):
        return "Empty string passed for one or more arguments"

    geniutil = pm.getService('geniutil')
    resource_manager_tools = pm.getService('resourcemanagertools')
    urn = geniutil.encode_urn(AUTHORITY, 'user', str(user_name))
    lookup_result = resource_manager_tools.object_lookup(AUTHORITY_NAME, 'key', {'KEY_MEMBER' : urn}, [])

    if public_key:
        if not lookup_result:

        # Generating The Credentials (TO-DO | Solve Problems with geni_utils)
            ma_c = read_file(KEY_PATH + MA_CERT_FILE)
            ma_pr = read_file(KEY_PATH + MA_KEY_FILE)
            u_c,u_pu,u_pr = geniutil.create_certificate(urn, issuer_key=ma_pr, issuer_cert=ma_c,
                                                        email=str(user_email))
            user_cred = geniutil.create_credential_ex(u_c, u_c, ma_pr, ma_c, privileges, CRED_EXPIRY)

        # Receiving public key and saving it in the Member Authority Data-base
            resource_manager_tools = pm.getService('resourcemanagertools')
            ssh_public_key = public_key
            registration_fields_member = dict( MEMBER_URN = urn,
                                       MEMBER_FIRSTNAME = first_name,
                                       MEMBER_LASTNAME 	= last_name,
                                       MEMBER_USERNAME =  user_name ,
                                       MEMBER_EMAIL =user_email,
                                       MEMBER_CERTIFICATE = u_c,
                                       MEMBER_CREDENTIALS = user_cred)

            registration_fields_key = dict(KEY_MEMBER= urn,
                                       KEY_TYPE = 'rsa-ssh',
                                       KEY_DESCRIPTION='SSH key for user ' + user_name,
                                       KEY_PUBLIC= ssh_public_key,
                                       KEY_ID= hashlib.sha224(ssh_public_key).hexdigest())

            resource_manager_tools.object_create(AUTHORITY_NAME, registration_fields_key, 'key')
            resource_manager_tools.object_create(AUTHORITY_NAME, registration_fields_member, 'member')

            registration_fields_member['MEMBER_CERTIFICATE_PRIVATE_KEY'] = u_pr
            return registration_fields_member, registration_fields_key
            #return u_c, u_pr, user_cred
        else:
            return "User already registered, try looking up the user with its URN instead !!"

    return "Public key missing, please provide you public key"

def runServer():
    """
    Run the registration Server
    """

    print "Waiting For Registration Requests...!!"
    server = RegistrationAppServer((registration_server_ip, int(registration_server_port)))
    server.register_function(register_user)
    server.serve_forever()
