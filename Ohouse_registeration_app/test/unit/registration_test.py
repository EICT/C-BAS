import jsonrpclib
from testtools import *
import unittest

class TestRegApp(unittest.TestCase):
    server_ip, server_port = get_server_conf('registration_app_config.json')
    server = jsonrpclib.Server('http://%s:%s' % (server_ip, server_port))


    def test_register_with_non_unique_username(self):
        '''
        Registration with non-unique user names should not be allowed
        :return:
        '''

        first_name = ['TestFirstName_100', 'TestFirstName_101']
        last_name =  ['TestLastName_100' , 'TestLastName_101']
        email     =  ['test_100@test.de',  'test_101@test.de']
        user_name =  'test_username_100'

        for index in range(0, 2):
            public_key_value, private_key_value = get_ssh_keys(first_name[index], last_name[index]) #create unique public private key pair
            ret_values = self.server.register_user(first_name[index],
                                                    last_name[index],
                                                    user_name,
                                                    email[index],
                                                    public_key_value)
            if len(ret_values) == 2:
                member, key = ret_values[:2]
            else:
                member = None

            # First registration has unique parameters so it should succeed
            if index == 0:
                self.assertIsNotNone(member)

            # First registration has non-unique user_name so it should fail
            if index == 1:
                self.assertIsNone(member)

    def test_register_with_non_unique_email(self):
        '''
        User registration is allowed for non-unique email address as long as user name and public key is unique
        :return:
        '''

        first_name = ['TestFirstName_200', 'TestFirstName_201']
        last_name =  ['TestLastName_200' , 'TestLastName_201']
        user_name =  ['test_username_200', 'test_username_201']
        email     =  'test_200@test.de'

        for index in range(2):
            public_key_value, private_key_value = get_ssh_keys(first_name[index], last_name[index]) #create unique public private key pair
            ret_values = self.server.register_user(first_name[index],
                                                    last_name[index],
                                                    user_name[index],
                                                    email,
                                                    public_key_value)
            if len(ret_values) == 2:
                member, key = ret_values[:2]
            else:
                member = None

            #Registration should succeed for all combinations
            self.assertIsNotNone(member)


    def test_register_with_non_unique_public_key(self):
        '''
        User registration should fail if non-unique public is provided
        '''

        first_name = ['TestFirstName_300', 'TestFirstName_301']
        last_name =  ['TestLastName_300', 'TestLastName_301']
        user_name =  ['test_username_300', 'test_username_301']
        email =      ['test_300@test.de', 'test_301@test.de']
        public_key_value = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDLpbEIycnsX7/pm1cC3TonZLU/AIlFujPvPL+68d3VShw1QkBNBJgqIRo9wPqz6B31HzkBpwkmdFkZQqhWUbvbnllgEK8sIvZ4a9u2ZsRI5qvoc9qDTS/kpRLajivBGH5quNAFBE5LSmkV29/pOOzJTO4XLMp8xAfCwq8s4hNdbZWpmX9/1GrC9yUckmchpD2YKVDrVqneCH3PlbB2XLmE1UIP98ic/Y3FXAwX5bS/i+k27N8TWlPSWV4I9MZkN4sVAIt99yjxJZtimWBm0fYZAEfDS57G58fpPTamQV2RWq1iNl6X9DxufxRQqHVRlo9ixKp1TTfkvCvH//PSLi+r test@test.de'
        ret_values = self.server.register_user(first_name[0],
                                               last_name[0],
                                               user_name[0],
                                               email[0],
                                               public_key_value)

        if len(ret_values) == 2:
            member, key = ret_values[:2]
        else:
            member = None

        #Registration should succeed for unique public key
        self.assertIsNotNone(member)

        ret_values = None
        try:
            ret_values = self.server.register_user(first_name[1],
                                                   last_name[1],
                                                   user_name[1],
                                                   email[1],
                                                   public_key_value)
        except Exception:
            pass

        #Registration should fail for non-unique public key
        self.assertIsNone(ret_values)


    def test_register_with_first_and_last_name_combinations(self):
        """
        User registration should be possible for any combination of First and Last names as long as
        user names and public keys are unique
        """
        # define name combinations
        first_name = ['TestFirstName_A', 'TestFirstName_A', 'TestFirstName_B', 'TestFirstName_B']
        last_name =  ['TestLastName_A',  'TestLastName_B',  'TestLastName_A',  'TestLastName_B']

        #define unique user names and email addresses
        user_name = ['test_username_A', 'test_username_B', 'test_username_C', 'test_username_D']
        email     = ['test_A@test.de', 'test_B@test.de', 'test_C@test.de', 'test_D@test.de']

        #All registration attempts should succeed in the this loop because First and Last name combinations are unique
        for index in range(0, 4):
            public_key_value, private_key_value = get_ssh_keys(first_name[index], last_name[index])
            ret_values = self.server.register_user(first_name[index],
                                                    last_name[index],
                                                    user_name[index],
                                                    email[index],
                                                    public_key_value)
            if len(ret_values) == 2:
                member, key = ret_values[:2]
            else:
                member = None

            #Registration should succeed for all combinations
            self.assertIsNotNone(member)

        #Redefine user names to make them unique
        user_name = ['test_username_E', 'test_username_F', 'test_username_G', 'test_username_H']

        #All registration attempts should succeed in the this loop because user names are unique though First and Last name combinations are already registered
        for index in range(0, 4):
            public_key_value, private_key_value = get_ssh_keys(first_name[index], last_name[index])
            ret_values = self.server.register_user(first_name[index],
                                                                last_name[index],
                                                                user_name[index],
                                                                email[index],
                                                                public_key_value)
            if len(ret_values) == 2:
                member, key = ret_values[:2]
            else:
                member = None

            #Registration should succeed for all combinations
            self.assertIsNotNone(member)

    def test_register_with_empty_argument(self):
        """
        User registration should not be possible if any of the necessary arguments are missing, i.e.,
        First and Last name, user name, email address.
        """
        first_name = ['', 'TestFirstName_401', 'TestFirstName_402', 'TestFirstName_403']
        last_name =  ['TestLastName_400',  '',  'TestLastName_402',  'TestLastName_403']
        user_name = ['test_username_400', 'test_username_401', '', 'test_username_403']
        email     = ['test_400@test.de', 'test_401@test.de', 'test_402@test.de', '']

        #All registration attempts should fail in the this loop because of missing details
        for index in range(0, 4):
            public_key_value, private_key_value = get_ssh_keys(first_name[index], last_name[index])
            ret_values = self.server.register_user(first_name[index],
                                                    last_name[index],
                                                    user_name[index],
                                                    email[index],
                                                    public_key_value)
            if len(ret_values) == 2:
                member, key = ret_values[:2]
            else:
                member = None

            #Registration should fail for all combinations
            self.assertIsNone(member)

    # def test_create_root_user(self):
    #     """
    #     Creates a root user
    #     :return:
    #     """
    #     privileges = "PROJECT_CREATE, GLOBAL_PROJECTS_WILDCARDS, GLOBAL_SLICES_WILDCARDS, GLOBAL_MEMBERS_WILDCARDS, SERVICE_REGISTER, SERVICE_REMOVE, SERVICE_VIEW, MEMBER_SET_LEAD_ROLE, GLOBAL_PROJECTS_VIEW, GLOBAL_PROJECTS_MONITOR, GLOBAL_SLICES_VIEW, GLOBAL_SLICES_MONITOR, MEMBER_REGISTER, MEMBER_REMOVE_REGISTRATION"
    #     public_key_value, private_key_value = get_ssh_keys("System", "Root")
    #     ret_values = self.server.register_user("System",
    #                                             "Root",
    #                                             "root",
    #                                             "root@eisland.de",
    #                                             public_key_value,
    #                                             privileges)
    #     if len(ret_values) == 3:
    #         member, key, credentials = ret_values[:3]
    #     else:
    #         credentials = None
    #
    #     self.assertIsNotNone(credentials)
    #
    #     write_file("root-cred.xml", credentials)
    #     write_file("root-cert.pem", member)
    #     write_file("root-key.pem", key)

if __name__ == '__main__':
    unittest.main(verbosity=0, exit=True)
