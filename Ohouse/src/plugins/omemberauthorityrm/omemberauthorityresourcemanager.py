import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('omemberauthorityrm')

import hashlib

from omemberauthorityexceptions import *
#<UT>
from amsoil.config import  expand_amsoil_path
from apiexceptionsv2 import *
import OpenSSL.crypto as crypto
import datetime as dt


class OMemberAuthorityResourceManager(object):
    """
    Manage Member Authority objects and resources.

    Generates neccessary fields when creating a new object.
    """
    #<UT>
    MA_CERT_FILE = 'ma-cert.pem'
    MA_KEY_FILE = 'ma-key.pem'
    CERT_VALIDITY_PERIOD = 600 # Days
    CRL_VALIDITY_PERIOD = 1 # Days
    AUTHORITY_NAME = 'ma' #: The short-name for this authority

    SUPPORTED_SERVICES = ['MEMBER', 'KEY'] #: The objects supported by this authority

    SUPPORTED_CREDENTIAL_TYPES = [{"type" : "SFA", "version" : 1}] #: The credential type supported by this authority

    def __init__(self):
        """
        Get plugins for use in other class methods.

        Set unique keys.
        """
        super(OMemberAuthorityResourceManager, self).__init__()
        self._resource_manager_tools = pm.getService('resourcemanagertools')
        self._set_unique_keys()
        #<UT>
        config = pm.getService("config")
        cert_path = expand_amsoil_path(config.get("delegatetools.trusted_cert_path"))
        cert_key_path = expand_amsoil_path(config.get("delegatetools.trusted_cert_keys_path"))
        hostname = config.get('flask.cbas_hostname')
        self._ma_crl_path = expand_amsoil_path(config.get("delegatetools.trusted_crl_path")) + '/' \
                                                    + hostname + '.authority.ma'
        print self._ma_crl_path
        self._ma_cert_str = self._resource_manager_tools.read_file(cert_path + '/' +
                                                            OMemberAuthorityResourceManager.MA_CERT_FILE)
        self._ma_cert_key_str = self._resource_manager_tools.read_file(cert_key_path + '/' +
                                                             OMemberAuthorityResourceManager.MA_KEY_FILE)

        self.gfed_ex = pm.getService('apiexceptionsv2')
        self._urn = self.urn()

        self._cert_revoke_reasons = crypto.Revoked().all_reasons()
        self._ma_cert = crypto.load_certificate(crypto.FILETYPE_PEM, self._ma_cert_str)
        self._ma_cert_key = crypto.load_privatekey(crypto.FILETYPE_PEM, self._ma_cert_key_str)

    def _set_unique_keys(self):
        """
        Set the required unique keys in the database for a Member Authority.
        """
        self._resource_manager_tools.set_index(self.AUTHORITY_NAME, 'MEMBER_UID')
        self._resource_manager_tools.set_index(self.AUTHORITY_NAME, 'MEMBER_URN')
        self._resource_manager_tools.set_index(self.AUTHORITY_NAME, 'KEY_ID')
        self._resource_manager_tools.set_index(self.AUTHORITY_NAME, 'CERT_SERIAL_NUMBER')

    #--- 'get_version' methods
    def urn(self):
        """
        Get the URN for this Member Authority.

        Retrieve the hostname from the Flask AMsoil plugin and use this to build
        the URN.

        """
        config = pm.getService('config')
        hostname = config.get('flask.cbas_hostname')
        return 'urn:publicid:IDN+' + hostname + '+authority+ma'

    def implementation(self):
        """
        Get the implementation details for this Member Authority.

        Retrieve details from the AMsoil plugin and form them into a dictionary
        suitable for the API call response.

        """
        manifest = pm.getManifest('omemberauthorityrm')
        if len(manifest) > 0:
            return {'code_version' : str(manifest['version'])}
        else:
            return None

    def services(self):
        """
        Return the services implemented by this Member Authority.
        """
        return self.SUPPORTED_SERVICES

    def api_versions(self):
        """
        Get the different endpoints (of type 'ma'), registered with AMsoil.

        Form these endpoints into a dictionary suitable for the API call response.

        """
        config = pm.getService('config')
        hostname = config.get('flask.hostname')
        port = str(config.get('flask.app_port'))
        endpoints = pm.getService('apitools').get_endpoints(type=self.AUTHORITY_NAME)
        return self._resource_manager_tools.form_api_versions(hostname, port,
            endpoints)

    def credential_types(self):
        """
        Return the credential types implemented by this Member Authority.
        """
        return self.SUPPORTED_CREDENTIAL_TYPES

    def fields(self):
        """
        Return the combined supplementary fields applicable to this Member Authority.
        """
        return self._resource_manager_tools.supplementary_fields(self.SUPPLEMENTARY_FIELDS)

    #--- object methods
    def update_member(self, urn, client_cert, credentials, fields, options):
        """
        Update a member object.
        """
        return self._resource_manager_tools.object_update(self.AUTHORITY_NAME,
            fields, 'member', {'MEMBER_URN':urn})

    def lookup_member(self, client_cert, credentials, match, filter_, options):
        """
        Lookup an a member(s).
        """
        return  self._resource_manager_tools.object_lookup(self.AUTHORITY_NAME,
            'member', match, filter_)

    def create_key(self, client_cert, credentials, fields, options):
        """
        Create a key object.

        Generate fields for a new object:
            * KEY_ID: hash of the existing 'KEY_PUBLIC' value

        """
        fields['KEY_ID'] = hashlib.sha224(fields['KEY_PUBLIC']).hexdigest()
        return self._resource_manager_tools.object_create(self.AUTHORITY_NAME,
            fields, 'key')

    def update_key(self, urn, client_cert, credentials, fields, options):
        """
        Update a key object.
        """
        return self._resource_manager_tools.object_update(self.AUTHORITY_NAME,
            fields, 'key', {'KEY_MEMBER': urn})

    def lookup_key(self, client_cert, credentials, match, filter_, options):
        """
        Lookup a key object.
        """
        return self._resource_manager_tools.object_lookup(self.AUTHORITY_NAME,
            'key', match, filter_)

    def delete_key(self, urn, client_cert, credentials, options):
        """
        Delete a key object.
        """
        return self._resource_manager_tools.object_delete(self.AUTHORITY_NAME,
            'key', {'KEY_ID':urn})

    def _issue_cert_serial_num(self):
        """
        Issues a unique serial number for member certificate to be generated
        :return: unique serial number
        """
        result = self._resource_manager_tools.object_lookup(self.AUTHORITY_NAME,
            'properties', {'URN': self._urn}, ['SERIAL_NUMBER_COUNTER'])

        if result:
            serial_number = result[0]['SERIAL_NUMBER_COUNTER']
            self._resource_manager_tools.object_update(self.AUTHORITY_NAME,
            {'SERIAL_NUMBER_COUNTER': serial_number+1}, 'properties', {'URN': self._urn})
        else:
            serial_number = 1
            self._resource_manager_tools.object_create(self.AUTHORITY_NAME,
                {'SERIAL_NUMBER_COUNTER': serial_number+1, 'URN': self._urn}, 'properties')

        return serial_number

    def revoke_certificate(self, urn, reason='unspecified'):
        """
        Revokes membership by revoking member certificate
        :param urn: member urn
        :return:
        """

        lookup_result = self._resource_manager_tools.object_lookup(self.AUTHORITY_NAME, 'member', {'MEMBER_URN' : urn}, [])
        if not lookup_result:
            raise self.gfed_ex.GFedv2ArgumentError("Specified user does not exist")

        if not reason in self._cert_revoke_reasons:
            raise self.gfed_ex.GFedv2ArgumentError("Unsupported reason for revoking certificate")

        member_cert = crypto.load_certificate(crypto.FILETYPE_PEM, lookup_result[0]['MEMBER_CERTIFICATE'])
        serial_number = member_cert.get_serial_number()
        expiration_date = member_cert.get_notAfter()
        now = dt.datetime.utcnow()
        cert_validity = dt.datetime.strptime(expiration_date, '%Y%m%d%H%M%SZ')

        if cert_validity > now:
            revoke_date = dt.datetime.utcnow().strftime('%Y%m%d%H%M%SZ') #GMT time in UTC format
            self._resource_manager_tools.object_create(self.AUTHORITY_NAME,
                    {'CERT_SERIAL_NUMBER': serial_number, 'REVOKE_REASON': reason, 'REVOKE_DATE': revoke_date,
                     'CERT_VALID_UNTIL': expiration_date}, 'crl')
            crl_pem_text = self.generate_crl()
            with open(self._ma_crl_path, 'w') as f:
                f.write(crl_pem_text)

    def generate_crl(self):
        """
        Generates Certificate Revocation List
        :return: CRL in PEM format
        """

        lookup_results = self._resource_manager_tools.object_lookup(self.AUTHORITY_NAME, 'crl', {}, [])
        crl = crypto.CRL()
        now = dt.datetime.utcnow()

        for entry in lookup_results:
            cert_expiration_date = dt.datetime.strptime(entry['CERT_VALID_UNTIL'], '%Y%m%d%H%M%SZ')
            if cert_expiration_date > now:
                revoked_entry = crypto.Revoked()
                revoked_entry.set_serial(hex(entry['CERT_SERIAL_NUMBER'])[2:])
                revoked_entry.set_reason(str(entry['REVOKE_REASON']))
                revoked_entry.set_rev_date(str(entry['REVOKE_DATE']))
                crl.add_revoked(revoked_entry)
            else:
                self._resource_manager_tools.object_delete(self.AUTHORITY_NAME,
                'crl', {'CERT_SERIAL_NUMBER': entry['CERT_SERIAL_NUMBER']})

        return crl.export(self._ma_cert, self._ma_cert_key, days=self.CRL_VALIDITY_PERIOD)

    def renew_membership(self, urn):
        """
        Renew membership through certificate and credential renewal
        :param urn: user urn
        :return:
        """
        lookup_result = self._resource_manager_tools.object_lookup(self.AUTHORITY_NAME, 'member', {'MEMBER_URN' : urn}, [])
        if not lookup_result:
            raise self.gfed_ex.GFedv2ArgumentError("Specified user does not exist")

        member_details = lookup_result[0]

        user_email = member_details['MEMBER_EMAIL']

        geniutil = pm.getService('geniutil')
        cred_expiry = dt.datetime.utcnow() + dt.timedelta(days=self.CERT_VALIDITY_PERIOD)
        u_c,u_pu,u_pr = geniutil.create_certificate(urn=urn, issuer_key=self._ma_cert_key_str,
                                                    issuer_cert=self._ma_cert_str, email=str(user_email),
                                                    serial_number= self._issue_cert_serial_num(),
                                                    life_days=self.CERT_VALIDITY_PERIOD)

        privileges, _ = geniutil.get_privileges_and_target_urn([{'SFA': member_details['MEMBER_CREDENTIALS']}])
        u_cred = geniutil.create_credential_ex(owner_cert=u_c, target_cert=u_c, issuer_key=self._ma_cert_key_str,
                                               issuer_cert=self._ma_cert_str, privileges_list=privileges,
                                               expiration=cred_expiry)

        self.revoke_certificate(urn, 'superseded')
        member_details['MEMBER_CERTIFICATE'] = u_c
        member_details['MEMBER_CREDENTIALS'] = u_cred
        self.update_member(urn=urn, client_cert=None, credentials=None, fields=member_details, options=None)

        # Add certificate key to return values
        member_details['MEMBER_CERTIFICATE_KEY'] = u_pr

        return member_details

    def register_member(self, certificate, credentials, fields, options):
        """
        Register user to member authority without any privileges

        Args:
            first_name: The first name of the user which will be included in the URN
            last_name: The last name of the user which will be included in the URN
            username: A name that might be used to reference a certain user
            email : The User Email
            public_key: An optional field, allows a user-generated public key

        Return:
            User generated data such as usrn, credentials, etc.
        """
        first_name = fields['MEMBER_FIRSTNAME']
        last_name = fields['MEMBER_LASTNAME']
        user_name = fields['MEMBER_USERNAME']
        user_email = fields['MEMBER_EMAIL']

        if 'KEY_PUBLIC' in fields:
            public_key = fields['KEY_PUBLIC']
        else:
            public_key = None

        privileges = []
        if 'privileges' in options:
            if 'CAN_CREATE_PROJECT' in options['privileges']:
                privileges = ['PROJECT_CREATE']

        geniutil = pm.getService('geniutil')
        config = pm.getService('config')
        hostname = config.get('flask.cbas_hostname')

        u_urn = geniutil.encode_urn(hostname, 'user', str(user_name))
        lookup_result = self._resource_manager_tools.object_lookup(self.AUTHORITY_NAME, 'member', {'MEMBER_URN' : u_urn}, [])

        if not lookup_result:
            cred_expiry = dt.datetime.utcnow() + dt.timedelta(days=self.CERT_VALIDITY_PERIOD)
            u_c,u_pu,u_pr = geniutil.create_certificate(urn=u_urn, issuer_key=self._ma_cert_key_str,
                                                        issuer_cert=self._ma_cert_str, email=str(user_email),
                                                        serial_number= self._issue_cert_serial_num(),
                                                        life_days=self.CERT_VALIDITY_PERIOD)
            u_cred = geniutil.create_credential_ex(owner_cert=u_c, target_cert=u_c, issuer_key=self._ma_cert_key_str,
                                                   issuer_cert=self._ma_cert_str, privileges_list=privileges,
                                                   expiration=cred_expiry)
            registration_fields_member = dict( MEMBER_URN = u_urn,
                                               MEMBER_FIRSTNAME = first_name,
                                               MEMBER_LASTNAME 	= last_name,
                                               MEMBER_USERNAME =  user_name ,
                                               MEMBER_EMAIL =user_email,
                                               MEMBER_CERTIFICATE = u_c,
                                               MEMBER_CREDENTIALS = u_cred,
                                               )
            self._resource_manager_tools.object_create(self.AUTHORITY_NAME, registration_fields_member, 'member')

            # Add certificate key to return values
            registration_fields_member['MEMBER_CERTIFICATE_KEY'] = u_pr

            #Register public key if provided
            if public_key:
                registration_fields_key = dict(KEY_MEMBER= u_urn,
                                               KEY_TYPE = 'rsa-ssh',
                                               KEY_DESCRIPTION='SSH key for user ' + user_name,
                                               KEY_PUBLIC= public_key,
                                               KEY_ID= hashlib.sha224(public_key).hexdigest())
                self._resource_manager_tools.object_create(self.AUTHORITY_NAME, registration_fields_key, 'key')
                self.renew_membership(u_urn)
                return dict(registration_fields_member, **registration_fields_key)
            else:
                return registration_fields_member

        else:
            raise self.gfed_ex.GFedv2DuplicateError("User already registered, try looking up the user with his URN instead !!")
