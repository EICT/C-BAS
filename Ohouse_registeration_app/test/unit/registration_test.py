import jsonrpclib
from testtools import *
import unittest

class TestRegApp(unittest.TestCase):

    def test_register_with_given_public_key(self):
        server_ip, server_port = get_server_conf('registration_app_config.json')
        print('Connecting to ' + server_ip + ':' + server_port + '...')
        server = jsonrpclib.Server('http://%s:%s' % (server_ip, server_port))
        first_name = 'TestFirstName1'
        last_name = 'TestLastName1'
        user_name = 'test_username1'
        email = 'test1@test.de'
        public_key_value = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDLpbEIycnsX7/pm1cC3TonZLU/AIlFujPvPL+68d3VShw1QkBNBJgqIRo9wPqz6B31HzkBpwkmdFkZQqhWUbvbnllgEK8sIvZ4a9u2ZsRI5qvoc9qDTS/kpRLajivBGH5quNAFBE5LSmkV29/pOOzJTO4XLMp8xAfCwq8s4hNdbZWpmX9/1GrC9yUckmchpD2YKVDrVqneCH3PlbB2XLmE1UIP98ic/Y3FXAwX5bS/i+k27N8TWlPSWV4I9MZkN4sVAIt99yjxJZtimWBm0fYZAEfDS57G58fpPTamQV2RWq1iNl6X9DxufxRQqHVRlo9ixKp1TTfkvCvH//PSLi+r test@test.de'

        member, key, credentials = server.register_user(first_name,
                                                       last_name,
                                                       user_name,
                                                       email,
                                                       public_key_value)

        return 0 if credentials else 200

    def test_register_without_given_public_key(self):
        server_ip, server_port = get_server_conf('registration_app_config.json')
        server = jsonrpclib.Server('http://%s:%s' % (server_ip, server_port))
        first_name = 'TestFN2'
        last_name = 'TestLN2'
        user_name = 'test_username2'
        email = 'test2@test.de'
        public_key_value, private_key_value = get_ssh_keys(first_name, last_name)

        member, key, credentials = server.register_user(first_name,
                                                       last_name,
                                                       user_name,
                                                       email,
                                                       public_key_value)

        return 0 if credentials else 200


if __name__ == '__main__':
    unittest.main(verbosity=0, exit=True)
