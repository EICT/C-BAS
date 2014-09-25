__author__ = 'umar.toseef'

import OpenSSL.crypto

from certgen import *


KEY_PATH = '../test/creds/'
AUTHORITY_NAME = 'ca'

AUTHORITY="ohouse:fp7-alien:eu"
CA_CERT_FILE = 'ca-cert.pem'
CA_KEY_FILE = 'ca-key.pem'

print "---------------------------------"
print "|Welcome to Ohouse Admin Console|"
print "---------------------------------\n"
print "Please enter the details to generate an SSL certificate\n"


def recursive_input(string_too_ask):
    output = raw_input(string_too_ask)
    while not output:
        output = recursive_input(string_too_ask)
    return output

entity_cn = recursive_input("Name of the entity:")
contact_email = recursive_input("Contact email: ")
entity_urn = raw_input("URN of the entity (optional): ")
entity_uuid = raw_input("UUID of the entity (optional): ")


st_cert=open(KEY_PATH + CA_CERT_FILE, 'rt').read()
c=OpenSSL.crypto
ca_c=c.load_certificate(c.FILETYPE_PEM, st_cert)

st_key=open(KEY_PATH + CA_KEY_FILE, 'rt').read()
ca_pr=c.load_privatekey(c.FILETYPE_PEM, st_key)

pkey = createKeyPair(TYPE_RSA, 2048)
req = createCertRequest(pkey, CN=entity_cn, emailAddress=contact_email )

if not entity_urn or entity_uuid:
    cert = createCertificate(req, (ca_c, ca_pr), 1, (0, 60*60*24*365*5)) # five year
else:
    subjectAltName = 'URI:'+entity_urn+', URI:'+entity_uuid+', email:'+contact_email
    cert = createCertificate(req, (ca_c, ca_pr), 1, (0, 60*60*24*365*5), subjectAltName=subjectAltName)


open('./certs/%s-key.pem' % (entity_cn,), 'w').write(crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey))
open('./certs/%s-cert.pem' % (entity_cn,), 'w').write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

print "Your SSL certificate is as follows:\n", st_cert


