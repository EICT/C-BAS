import tempfile
import uuid
import os
import os.path
import shutil

from ext.geni.util.urn_util import URN
from ext.sfa.trust.gid import GID
# import ext.geni
from ext.sfa.trust.certificate import Keypair
from ext.geni.util import cert_util as gcf_cert_util
from ext.geni.util import cred_util as gcf_cred_util
import ext.sfa.trust.credential as sfa_cred
import ext.sfa.trust.rights as sfa_rights
from ext.sfa.util.faults import SfaFault
import ext.geni
import xml.etree.ElementTree as ET
from types import StringTypes

def decode_urn(urn):
    """Returns authority, type and name associated with the URN as string.
    example call:
      authority, typ, name = decode_urn("urn:publicid:IDN+eict.de+user+motine")
    """
    urn = URN(urn=str(urn))
    return urn.getAuthority(), urn.getType(), urn.getName()

def encode_urn(authority, typ, name, project=None):
    """
    Returns a URN string with the given {authority}, {typ}e and {name}.
    {typ} shall be either of the following: authority, slice, user, sliver, (project or meybe others: http://groups.geni.net/geni/wiki/GeniApiIdentifiers#Type)
    example call:
      urn_str = encode_urn("eict.de", "user", "motine")
    """
    if project and typ == 'slice':
        authority_ = authority+':'+project
    else:
        authority_ = authority

    return URN(authority=authority_, type=typ, name=name).urn_string()

def create_certificate(urn, issuer_key=None, issuer_cert=None, is_ca=False,
                       public_key=None, life_days=1825, email=None, uuidarg=None, serial_number=0):
    """Creates a certificate.
    {issuer_key} private key of the issuer. can either be a string in pem format or None.
    {issuer_cert} can either be a string in pem format or None.
    If either {issuer_cert} or {issuer_key} is None, the cert becomes self-signed
    {public_key} contains the pub key which will be embedded in the certificate. If None a new key is created, otherwise it must be a string)
    {uuidarg} can be a uuid.UUID or a string.

    Returns tuple in the following order:
      x509 certificate in PEM format
      public key of the keypair related to the new certificate in PEM format
      public key of the keypair related to the new certificate in PEM format or None if the the {public_key} was given.

    IMPORTANT
    Do not add an email when creating sa/ma/cm. This may lead to unverificable certs later.
    """
    # create temporary files for some params, because gcf's create_cert works with files and I did not want to duplicate the code
    pub_key_param = None
    if public_key:
        fh, pub_key_param = tempfile.mkstemp(); os.write(fh, public_key); os.close(fh)
    issuer_key_param, issuer_cert_param = None, None
    if issuer_key and issuer_cert:
        fh, issuer_key_param = tempfile.mkstemp(); os.write(fh, issuer_key); os.close(fh)
        fh, issuer_cert_param = tempfile.mkstemp(); os.write(fh, issuer_cert); os.close(fh)

    cert_gid, cert_keys = gcf_cert_util.create_cert(urn, issuer_key_param, issuer_cert_param, is_ca, pub_key_param,
                                                    life_days, email, uuidarg, serial_number)
    if pub_key_param:
        os.remove(pub_key_param)
    if issuer_key_param:
        os.remove(issuer_key_param)
    if issuer_cert_param:
        os.remove(issuer_cert_param)

    priv_key_result = None
    if not public_key:
        priv_key_result = cert_keys.as_pem()
    return cert_gid.save_to_string(), cert_keys.get_m2_pkey().get_rsa().as_pem(), priv_key_result

def create_slice_certificate(slice_urn, issuer_key, issuer_cert, expiration):
    """Returns only the x509 certificate as string (as PEM)."""
    return create_certificate(slice_urn, issuer_key, issuer_cert, uuidarg=uuid.uuid4())[0]

def create_credential(owner_cert, target_cert, issuer_key, issuer_cert, typ, expiration, delegatable=False):
    """
    {expiration} can be a datetime.datetime or a int/float (see http://docs.python.org/2/library/datetime.html#datetime.date.fromtimestamp) or a string with a UTC timestamp in it
    {typ} is used to determine the rights (via ext/sfa/truse/rights.py) can either of the following: "user", "sa", "ma", "cm", "sm", "authority", "slice", "component" also you may specify "admin" for all privileges.
    Returns the credential as String
    """
    ucred = sfa_cred.Credential()
    ucred.set_gid_caller(GID(string=owner_cert))
    ucred.set_gid_object(GID(string=target_cert))
    ucred.set_expiration(expiration)

    if typ == "admin":
        if delegatable:
            raise ValueError("Admin credentials can not be delegatable")
        privileges = sfa_rights.Rights("*")
    else:
        privileges = sfa_rights.determine_rights(typ, None)
        privileges.delegate_all_privileges(delegatable)
    ucred.set_privileges(privileges)
    ucred.encode()

    issuer_key_file, issuer_key_filename = tempfile.mkstemp(); os.write(issuer_key_file, issuer_key); os.close(issuer_key_file)
    issuer_cert_file, issuer_cert_filename = tempfile.mkstemp(); os.write(issuer_cert_file, issuer_cert); os.close(issuer_cert_file)

    ucred.set_issuer_keys(issuer_key_filename, issuer_cert_filename) # priv, gid
    ucred.sign()

    os.remove(issuer_key_filename)
    os.remove(issuer_cert_filename)

    return ucred.save_to_string()

def create_credential_ex(owner_cert, target_cert, issuer_key, issuer_cert, privileges_list,
                         expiration, delegatable=True, parent_creds=None):
    """
    {expiration} can be a datetime.datetime or a int/float (see http://docs.python.org/2/library/datetime.html#datetime.date.fromtimestamp) or a string with a UTC timestamp in it
    {privileges_list} list of privileges as list
    Returns the credential as String
    """
    ucred = sfa_cred.Credential()
    ucred.set_gid_caller(GID(string=owner_cert))
    ucred.set_gid_object(GID(string=target_cert))
    ucred.set_expiration(expiration)

    #Check if delegated credentials have been requested
    if parent_creds:
        cred_obj = sfa_cred.Credential(string=parent_creds[0]['geni_value'])
        ucred.set_parent(cred_obj)

    privileges_str = ','.join(privileges_list)
    privileges = sfa_rights.Rights(privileges_str)
    privileges.delegate_all_privileges(delegatable)
    ucred.set_privileges(privileges)
    ucred.encode()

    issuer_key_file, issuer_key_filename = tempfile.mkstemp(); os.write(issuer_key_file, issuer_key); os.close(issuer_key_file)
    issuer_cert_file, issuer_cert_filename = tempfile.mkstemp(); os.write(issuer_cert_file, issuer_cert); os.close(issuer_cert_file)

    ucred.set_issuer_keys(issuer_key_filename, issuer_cert_filename) # priv, gid
    ucred.sign()

    os.remove(issuer_key_filename)
    os.remove(issuer_cert_filename)

    return ucred.save_to_string()

#<UT>
def extract_owner_certificate(credentials):
    owner_cert = None
    if credentials:
        cred_obj = sfa_cred.Credential(string=credentials if isinstance(credentials, StringTypes) else credentials[0]['geni_value'])
        owner_cert = cred_obj.get_gid_caller().save_to_string(save_parents=True)

    return owner_cert

def extract_object_certificate(credentials):
    object_cert = None
    if credentials:
        cred_obj = sfa_cred.Credential(string=credentials if isinstance(credentials, StringTypes) else credentials[0]['geni_value'])
        object_cert = cred_obj.get_gid_object().save_to_string(save_parents=True)
    return object_cert

def verify_credential_ex(credentials, target_urn, trusted_cert_path, privileges=(), crl_path=None):

    if credentials:
        cred_obj = sfa_cred.Credential(string=credentials[0]['geni_value'])
        owner_cert = extract_owner_certificate(credentials)
        if cred_obj.parent:
            verify_delegated_credentials(credentials, owner_cert, target_urn, trusted_cert_path, privileges, crl_path)
        else:
            verify_credential(credentials, owner_cert, target_urn, trusted_cert_path, privileges, crl_path)


def verify_delegated_credentials(credentials, owner_cert, target_urn, trusted_cert_path, privileges=(), crl_path=None):
    """
    Verified delegated creds by (1) verifying the original creds (2) verifying all included signatures
    :param credentials:
    :param owner_cert:
    :param target_urn:
    :param trusted_cert_path:
    :param privileges:
    :return:
    """
    #First verify original creds

    if credentials:
        ET.register_namespace('', "http://www.w3.org/2000/09/xmldsig#")
        root = ET.fromstring(credentials[0]['geni_value']) #FIXME: short-term solution to fix string handling, take first credential of SFA format
        cred_list = []
        for c in root.iter('credential'):
            cred_list.append(c)

        signs = root.find('signatures')
        o_sign = None
        sign_list = []
        for s in signs:
            sign_list.append(s)
            if 'Sig_ref0' in s.attrib.values():
                o_sign = s

        #Construct original cred text
        root.remove(root.find('credential'))
        root.remove(root.find('signatures'))
        #Add original creds
        root.append(cred_list[-1])
        #Get XML string including only original creds without signature part
        c_str = ET.tostring(root)
        #Get XML string for signature
        s_str = ET.tostring(o_sign)
        #Combine cred and signature parts to make final XML string
        d_str = c_str.replace('</signed-credential>', '')+'<signatures>'+s_str+'</signatures></signed-credential>'

        #Verify now the original creds
        o_cert = cred_list[-1][2].text
        t_cert = cred_list[-1][4].text
        urn, _, _ = extract_certificate_info(t_cert)
        verify_credential([{'geni_type': 'geni_sfa', 'geni_version':'3', 'geni_value': d_str}], o_cert, urn, trusted_cert_path, crl_path=crl_path)

        #Add necessary signatures certificates to the trusted path
        #Create tmp dir for use as trusted_path
        dir_path = os.path.normpath(os.path.join(trusted_cert_path, '../', 'tmp'))
        #Remove any existing contents
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        #Make a fresh dir
        os.mkdir(dir_path)

        #copy existing trusted certificates to that dir
        src_files = os.listdir(trusted_cert_path)
        for file_name in src_files:
            full_file_name = os.path.join(trusted_cert_path, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, dir_path)

        #Copy certificates extracted from delegated creds excluding the MA/SA certificate
        name_postfix = 0
        for s in sign_list:
            if not 'Sig_ref0' in s.attrib.values():
                name_postfix += 1
                path = os.path.join(dir_path, 'tmp'+str(name_postfix)+'-cert.pem')
                with open(path, "w") as f:
                    f.write('-----BEGIN CERTIFICATE-----\n'+s[2][0][0].text+'\n-----END CERTIFICATE-----')

        verify_credential(credentials, owner_cert, target_urn, dir_path, privileges, crl_path=crl_path)


def get_privileges_and_target_urn(credentials):
    """
    Provides a list of privileges included in the given credentials
    :param credentials: SFA formatted string
    :return: list of privileges
    """
    from types import StringTypes
    priv_list = []
    target_urn = None
    if credentials:
        cred_obj = sfa_cred.Credential(string=credentials if isinstance(credentials, StringTypes) else credentials[0]['geni_value'])
        target_urn = cred_obj.get_gid_object().get_urn()
        privileges = cred_obj.get_privileges().rights
        for p in privileges:
            priv_list.append(p.kind)

    return priv_list, target_urn

def get_expiration(credentials_str):
    """

    :param credentials:
    :return:
    """
    if credentials_str:
        cred_obj = sfa_cred.Credential(string=credentials_str)
        return cred_obj.get_expiration()
    else:
        return None


def extract_certificate_info(certificate):
    """Returns the urn, uuid and email of the given certificate."""
    user_gid = GID(string=certificate)
    user_urn = user_gid.get_urn()
    user_uuid = user_gid.get_uuid()
    user_email = user_gid.get_email()
    return user_urn, user_uuid, user_email

def get_serial_number(certificate):
    "Returns the serial number of given certificate"
    user_gid = GID(string=certificate)
    return user_gid.get_serial_number()


def verify_certificate(certificate, trusted_cert_path=None, crl_path=None):
    """
    Taken from ext...gid
    Verifies the chain of authenticity of the GID. First performs the checks of the certificate class (verifying that each parent signs the child, etc).
    In addition, GIDs also confirm that the parent's HRN is a prefix of the child's HRN, and the parent is of type 'authority'.

    Raises a ValueError if bad certificate.
    Does not return anything if successful.
    """
    try:
        trusted_certs = None
        if trusted_cert_path:
            trusted_certs_paths = [os.path.join(os.path.expanduser(trusted_cert_path), name) for name in os.listdir(os.path.expanduser(trusted_cert_path)) if (name != gcf_cred_util.CredentialVerifier.CATEDCERTSFNAME) and (name[0] != '.')]
            trusted_certs = [GID(filename=name) for name in trusted_certs_paths]
        gid = GID(string=certificate)
        gid.verify_chain(trusted_certs, crl_path)
    except SfaFault as e:
        raise ValueError("Error verifying certificate: %s" % (str(e),))
    return None

def verify_credential(credentials, owner_cert, target_urn, trusted_cert_path, privileges=(), crl_path=None):
    """
    Give a list of credentials and they will be checked to have the privleges and to be trusted by the trusted_certs.
    The privileges should be tuple.

    To verify a user: owner_cert=user_cert, target_urn=user
    To verify a slice: owner_cert=user_cert, target_urn=slice_urn


    {credentials} a list of strings (["CRED1", "CRED2"]) or a list of dictionaries [{"SFA" : "CRED1"}, {"ABAC" : "CRED2"}]
    {owner_cert} a string with the cert in PEM format
    {target_urn} a string with a urn
    {trusted_cert_path} a string containing the file system path with files (trusted certificates) in pem format in it
    {privileges} a list of the privileges (see below)

    Here a list of possible privileges (format: right_in_credential: [privilege1, privilege2, ...]):
        "authority" : ["register", "remove", "update", "resolve", "list", "getcredential", "*"],
        "refresh"   : ["remove", "update"],
        "resolve"   : ["resolve", "list", "getcredential"],
        "sa"        : ["getticket", "redeemslice", "redeemticket", "createslice", "createsliver", "deleteslice", "deletesliver", "updateslice",
                       "getsliceresources", "getticket", "loanresources", "stopslice", "startslice", "renewsliver",
                        "deleteslice", "deletesliver", "resetslice", "listslices", "listnodes", "getpolicy", "sliverstatus"],
        "embed"     : ["getticket", "redeemslice", "redeemticket", "createslice", "createsliver", "renewsliver", "deleteslice",
                       "deletesliver", "updateslice", "sliverstatus", "getsliceresources", "shutdown"],
        "bind"      : ["getticket", "loanresources", "redeemticket"],
        "control"   : ["updateslice", "createslice", "createsliver", "renewsliver", "sliverstatus", "stopslice", "startslice",
                       "deleteslice", "deletesliver", "resetslice", "getsliceresources", "getgids"],
        "info"      : ["listslices", "listnodes", "getpolicy"],
        "ma"        : ["setbootstate", "getbootstate", "reboot", "getgids", "gettrustedcerts"],
        "operator"  : ["gettrustedcerts", "getgids"],
        "*"         : ["createsliver", "deletesliver", "sliverstatus", "renewsliver", "shutdown"]

    When using the gcf clearinghouse implementation the credentials will have the rights:
    - user: "refresh", "resolve", "info" (which resolves to the privileges: "remove", "update", "resolve", "list", "getcredential", "listslices", "listnodes", "getpolicy").
    - slice: "refresh", "embed", "bind", "control", "info" (well, do the resolving yourself...)
    """
    # if client_cert == None:
    #     # work around if the certificate could not be acquired due to the shortcommings of the werkzeug library
    #     if config.get("flask.debug"):
    #         import ext.sfa.trust.credential as cred
    #         client_cert = cred.Credential(string=geni_credentials[0]).gidCaller.save_to_string(save_parents=True)
    #     else:
    #         raise GENIv3ForbiddenError("Could not determine the client SSL certificate")
    # test the credential
    creds = credentials # strip the type info if a list of dicts is given
    if len(credentials) > 0 and isinstance(credentials[0], dict):
        creds = [cred.values()[0] for cred in credentials]
    try:
        cred_verifier = ext.geni.CredentialVerifier(trusted_cert_path, crl_path)
        cred_verifier.verify_from_strings(owner_cert, creds, target_urn, privileges)
    except Exception as e:
        raise ValueError("Error verifying the credential: %s" % (str(e),))

def infer_client_cert(client_cert, credentials):
    """Returns client_cert if it is not None. It returns the first cert of the credentials if one is given.
    This is only needed to work around if the certificate could not be acquired due to the shortcommings of the werkzeug library.
    """
    import eisoil.core.log
    logger=eisoil.core.log.getLogger('geni_trust')

    import eisoil.core.pluginmanager as pm
    config = pm.getService('config')

    if client_cert != None:
        return client_cert
    elif config.get("flask.debug"):
        first_cred = credentials[0]
        first_cred_val = first_cred.values()[0]
        logger.warning("Infered client cert from credential as workaround missing feature in werkzeug")
        return sfa_cred.Credential(string=first_cred_val).gidCaller.save_to_string(save_parents=True)
    else:
        raise RuntimeError("The workaround could not determine the client SSL certificate (bloody werkzeug library! please try to use production mode)")
