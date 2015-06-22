import eisoil.core.pluginmanager as pm
import eisoil.core.log
logger=eisoil.core.log.getLogger('osliceauthorityrm')

import uuid
import pyrfc3339
import datetime
import pytz
from eisoil.config import  expand_eisoil_path

class OSliceAuthorityResourceManager(object):
    """
    Manage Slice Authority objects and resources.

    Generates neccessary fields when creating a new object.
    """
    SA_CERT_FILE = 'sa-cert.pem'
    SA_KEY_FILE = 'sa-key.pem'

    CRED_EXPIRY = datetime.datetime.utcnow() + datetime.timedelta(days=600)

    AUTHORITY_NAME = 'sa' #: The short-name for this authority
    SUPPORTED_SERVICES = ['SLICE', 'SLICE_MEMBER', 'SLIVER_INFO', 'PROJECT', 'PROJECT_MEMBER'] #: The objects supported by this authority
    SUPPORTED_CREDENTIAL_TYPES = [{"type" : "SFA", "version" : 1}] #: The credential type supported by this authority

    def __init__(self):
        """
        Get plugins for use in other class methods.

        Set unique keys.
        """
        super(OSliceAuthorityResourceManager, self).__init__()
        self._resource_manager_tools = pm.getService('resourcemanagertools')
        self._set_unique_keys()

        #<UT>
        config = pm.getService("config")
        cert_path = expand_eisoil_path(config.get("delegatetools.trusted_cert_path"))
        cert_key_path = expand_eisoil_path(config.get("delegatetools.trusted_cert_keys_path"))


        self._sa_c = self._resource_manager_tools.read_file(cert_path + '/' +
                                                            OSliceAuthorityResourceManager.SA_CERT_FILE)
        self._sa_pr = self._resource_manager_tools.read_file(cert_key_path + '/' +
                                                             OSliceAuthorityResourceManager.SA_KEY_FILE)

        #<UT>
        self._delegate_tools = pm.getService('delegatetools')
        self.gfed_ex = pm.getService('apiexceptionsv2')


    #--- 'get_version' methods
    def _set_unique_keys(self):
        """
        Set the required unique keys in the database for a Slice Authority.
        """
        #self._resource_manager_tools.set_index(self.AUTHORITY_NAME, 'SLICE_UID')
        #<UT> According to new structure SLICE_URN cannot be a unique key
        self._resource_manager_tools.set_index(self.AUTHORITY_NAME, 'SLICE_URN', unique=False)
        #self._resource_manager_tools.set_index(self.AUTHORITY_NAME, 'SLIVER_INFO_URN')
        #self._resource_manager_tools.set_index(self.AUTHORITY_NAME, 'PROJECT_UID')

        #<UT> According to new structure PROJECT_URN cannot be a unique key
        self._resource_manager_tools.set_index(self.AUTHORITY_NAME, 'PROJECT_URN', unique=False)

    def urn(self):
        """
        Get the URN for this Slice Authority.

        Retrieve the hostname from the Flask eiSoil plugin and use this to build
        the URN.

        """
        config = pm.getService('config')
        hostname = config.get('flask.cbas_hostname')
        return 'urn:publicid:IDN+' + hostname + '+authority+sa'

    def implementation(self):
        """
        Get the implementation details for this Slice Authority.

        Retrieve details from the eiSoil plugin and form them into a dictionary
        suitable for the API call response.

        """
        manifest = pm.getManifest('osliceauthorityrm')
        if len(manifest) > 0:
            return {'code_version' : str(manifest['version'])}
        else:
            return None

    def services(self):
        """
        Return the services implemented by this Slice Authority.
        """
        return self.SUPPORTED_SERVICES

    def api_versions(self):
        """
        Get the different endpoints (of type 'ma'), registered with eiSoil.

        Form these endpoints into a dictionary suitable for the API call response.

        """
        config = pm.getService('config')
        hostname = config.get('flask.hostname')
        port = str(config.get('flask.app_port'))
        endpoints = pm.getService('apitools').get_endpoints(type=self.AUTHORITY_NAME)
        return self._resource_manager_tools.form_api_versions(hostname, port, endpoints)

    def credential_types(self):
        """
        Return the  credential types implemented by this Slice Authority.
        """
        return self.SUPPORTED_CREDENTIAL_TYPES


    #--- object methods
    def create_slice(self, credentials, fields, options):
        """
        Create a slice object.

        Generate fields for a new object:
            * SLICE_URN: retrieve the hostname from the Flask eiSoil plugin
                and form into a valid URN
            * SLICE_UID: generate a new UUID4 value
            * SLICE_CREATION: get the time now and convert it into RFC3339 form
            * SLICE_EXPIRED: slice object has just been created, so it is has not
                yet expired
        """

        geniutil = pm.getService('geniutil')

        #<UT> Shall we enforce existence of project to which this new slice would belong?
        #The information about project is sent in fields under SLICE_PROJECT_URN key
        config = pm.getService('config')
        hostname = config.get('flask.cbas_hostname')
        _, _, project_name = geniutil.decode_urn(fields['SLICE_PROJECT_URN'])
        slice_urn = geniutil.encode_urn(hostname, 'slice', str(fields.get('SLICE_NAME')), project_name)

        lookup_results =  self._resource_manager_tools.object_lookup(self.AUTHORITY_NAME, 'slice', {'SLICE_URN': slice_urn}, {})
        if len(lookup_results) >0:
            raise self.gfed_ex.GFedv2ArgumentError("A slice with specified name already exists under the following URN "+ str(slice_urn))

        fields['SLICE_URN'] = slice_urn
        fields['SLICE_UID'] = str(uuid.uuid4())
        fields['SLICE_CREATION'] = pyrfc3339.generate(datetime.datetime.utcnow().replace(tzinfo=pytz.utc))
        fields['SLICE_EXPIRED'] = False

        if 'SLICE_EXPIRATION' in fields:
            expDate = datetime.datetime.strptime(fields['SLICE_EXPIRATION'], '%Y-%m-%dT%H:%M:%SZ')
            if expDate > self.CRED_EXPIRY:
                fields['SLICE_EXPIRATION'] = pyrfc3339.generate(self.CRED_EXPIRY.replace(tzinfo=pytz.utc))
        else:
            fields['SLICE_EXPIRATION'] = pyrfc3339.generate(self.CRED_EXPIRY.replace(tzinfo=pytz.utc))

        #Generating Slice certificate
        s_cert, s_pu, s_pr = geniutil.create_certificate(slice_urn, self._sa_pr, self._sa_c, life_days=3650)
        fields['SLICE_CERTIFICATE'] = s_cert

        #Try to get the user credentials for use as owner
        user_cert = geniutil.extract_owner_certificate(credentials)

        #Extract user info from his certificate
        user_urn, user_uuid, user_email = geniutil.extract_certificate_info(user_cert)

        #Get the privileges user would get as owner in the slice credential
        user_pri = self._delegate_tools.get_default_privilege_list(role_='LEAD', context_='SLICE')

        #For compatability with GAPI
        user_pri.extend(['*', 'refresh', 'embed', 'bind', 'control', 'info'])
        #Create slice cred for owner
        slice_cred = geniutil.create_credential_ex(owner_cert=user_cert, target_cert=s_cert, issuer_key=self._sa_pr,
                                                   issuer_cert=self._sa_c, privileges_list=user_pri, expiration=fields['SLICE_EXPIRATION'])

        #Let's make the owner as LEAD
        fields['SLICE_LEAD'] = user_urn

        #Finally, create slice object
        ret_values = self._resource_manager_tools.object_create(self.AUTHORITY_NAME, fields, 'slice')

        #Add slice credentials to the return values
        ret_values['SLICE_CREDENTIALS'] = slice_cred

        #Create SLICE_MEMBER object
        options = {'members_to_add' : [{'SLICE_MEMBER' : user_urn, 'SLICE_CREDENTIALS': slice_cred, 'SLICE_CERTIFICATE': s_cert, 'SLICE_ROLE': 'LEAD'}]}
        self._resource_manager_tools.member_modify(self.AUTHORITY_NAME, 'slice_member', slice_urn, options, 'SLICE_MEMBER', 'SLICE_URN')

        return ret_values

    def update_slice(self, urn, credentials, fields, options):
        """
        Update a slice object.
        """
        if 'SLICE_EXPIRATION' in fields:
            lookup_results = self.lookup_slice_membership(urn, credentials, {}, {}, options)
            for entry in lookup_results:
                newCred = self._update_cred_expiry(cred=entry['SLICE_CREDENTIALS'], obj_cert=entry['SLICE_CERTIFICATE'], expiry=fields['SLICE_EXPIRATION'])
                opt = {'members_to_change': [{'SLICE_MEMBER' : entry['SLICE_MEMBER'], 'SLICE_CREDENTIALS': newCred}]}
                self._resource_manager_tools.member_modify(self.AUTHORITY_NAME, 'slice_member', urn, opt, 'SLICE_MEMBER', 'SLICE_URN')

        return self._resource_manager_tools.object_update(self.AUTHORITY_NAME, fields, 'slice', {'SLICE_URN':urn})

    def lookup_slice(self, credentials, match, filter_, options):
        """
        Lookup a slice object.
        """
        return self._resource_manager_tools.object_lookup(self.AUTHORITY_NAME, 'slice', match, filter_)

    def create_sliver_info(self, credentials, fields, options):
        """
        Create a sliver information object.
        """
        return self._resource_manager_tools.object_create(self.AUTHORITY_NAME, fields, 'sliver_info')

    def update_sliver_info(self, urn, credentials, fields, options):
        """
        Update a sliver information object.
        """
        return self._resource_manager_tools.object_update(self.AUTHORITY_NAME, fields, 'sliver_info', {'SLIVER_INFO_URN':urn})

    def lookup_sliver_info(self, credentials, match, filter_, options):
        """
        Lookup a sliver information object.
        """
        return self._resource_manager_tools.object_lookup(self.AUTHORITY_NAME, 'sliver_info', match, filter_)

    def delete_sliver_info(self, urn, credentials, options):
        """
        Delete a sliver information object.
        """
        return self._resource_manager_tools.object_delete(self.AUTHORITY_NAME, 'sliver_info', {'SLIVER_INFO_URN':urn})

    def create_project(self, credentials, fields, options):
        """
        Create a project object.

        Generate fields for a new object:
            * PROJECT_URN: retrieve the hostname from the Flask eiSoil plugin
                and form into a valid URN
            * PROJECT_UID: generate a new UUID4 value
            * PROJECT_CREATION: get the time now and convert it into RFC3339 form
            * PROJECT_EXPIRED: project object has just been created, so it is
                has not yet expired

        """
        config = pm.getService('config')
        hostname = config.get('flask.cbas_hostname')
        p_urn = 'urn:publicid:IDN+' + hostname + '+project+' + fields.get('PROJECT_NAME')

        fields['PROJECT_URN'] = p_urn
        fields['PROJECT_UID'] = str(uuid.uuid4())
        fields['PROJECT_CREATION'] = pyrfc3339.generate(datetime.datetime.utcnow().replace(tzinfo=pytz.utc))
        fields['PROJECT_EXPIRED'] = False


        #<UT>
        geniutil = pm.getService('geniutil')
        #Generating Project Certificate
        p_cert, p_pu, p_pr = geniutil.create_certificate(p_urn, self._sa_pr, self._sa_c)
        fields['PROJECT_CERTIFICATE'] = p_cert

        #Try to get the user credentials for use as owner
        user_cert = geniutil.extract_owner_certificate(credentials)

        #Extract user info from his certificate
        user_urn, user_uuid_int, user_email = geniutil.extract_certificate_info(user_cert)
        #Get the privileges user would get as owner in the project credential
        user_pri = self._delegate_tools.get_default_privilege_list(role_='LEAD', context_='PROJECT')
        #Create project cred for owner
        p_creds = geniutil.create_credential_ex(owner_cert=user_cert, target_cert=p_cert, issuer_key=self._sa_pr, issuer_cert=self._sa_c, privileges_list=user_pri,
                                                    expiration=OSliceAuthorityResourceManager.CRED_EXPIRY)

        #Let's make the owner as LEAD
        fields['PROJECT_LEAD'] = user_urn

        #Finally, create project object
        ret_values = self._resource_manager_tools.object_create(self.AUTHORITY_NAME, fields, 'project')
        #Add Project credentials to ret values
        ret_values['PROJECT_CREDENTIALS'] = p_creds

        user_uuid = uuid.UUID(int=user_uuid_int).urn[9:]
        #Create PROJECT_MEMBER object
        options = {'members_to_add' : [{'PROJECT_MEMBER': user_urn, 'PROJECT_MEMBER_UID': user_uuid, 'PROJECT_CREDENTIALS': p_creds, 'PROJECT_CERTIFICATE': p_cert, 'PROJECT_ROLE': 'LEAD'}]}
        self._resource_manager_tools.member_modify(self.AUTHORITY_NAME, 'project_member', p_urn, options, 'PROJECT_MEMBER', 'PROJECT_URN')

        return ret_values


    def update_project(self, urn, credentials, fields, options):
        """
        Update a project object.
        """
        return self._resource_manager_tools.object_update(self.AUTHORITY_NAME, fields, 'project', {'PROJECT_URN':urn})

    def delete_project(self, urn, credentials, options):
        """
        Delete a project object.
        """

        slice_lookup_result = self.lookup_slice(None, match={'PROJECT_URN': urn}, filter_=[], options=None)

        if len(slice_lookup_result) > 0:
            raise self.gfed_ex.GFedv2ArgumentError("This project cannot be deleted as it has "+str(len(slice_lookup_result))+" active slices: "+ str(urn))
        member_lookup_result = self.lookup_project_membership(urn, credentials, {}, {}, None)

        #Remove all members including LEAD
        if len(member_lookup_result) > 0:
            remove_data = []
            for member in member_lookup_result:
                remove_data.append({'PROJECT_MEMBER' : member['PROJECT_MEMBER']})
        self._resource_manager_tools.member_modify(self.AUTHORITY_NAME, 'project_member', urn, {'members_to_remove': remove_data}, 'PROJECT_MEMBER', 'PROJECT_URN')


        return self._resource_manager_tools.object_delete(self.AUTHORITY_NAME, 'project', {'PROJECT_URN':urn})

    def lookup_project(self, credentials, match, filter_, options):
        """
        Lookup a project object.
        """
        return self._resource_manager_tools.object_lookup(self.AUTHORITY_NAME, 'project', match, filter_)

    def modify_slice_membership(self, urn, credentials, options):
        """
        Modify a slice membership object.
        """
        #<UT>
        slice_lookup_result = self.lookup_slice(None, match={'SLICE_URN':urn}, filter_=[], options=None)

        if not len(slice_lookup_result):
            raise self.gfed_ex.GFedv2ArgumentError("The specified slice does not exist "+ str(urn))
        if len(slice_lookup_result) > 1:
            raise self.gfed_ex.GFedv2DuplicateError("There are more than one instance of specified slice: "+ str(urn))

        slice_cert = slice_lookup_result[0]['SLICE_CERTIFICATE']
        slice_lead = slice_lookup_result[0]['SLICE_LEAD']

        geniutil = pm.getService('geniutil')
        owner_cert = geniutil.extract_owner_certificate(credentials)
        user_urn_from_cert, _, _ = geniutil.extract_certificate_info(owner_cert)
        _, target_urn_from_cred = geniutil.get_privileges_and_target_urn(credentials)

        #slice membership can be modified using
        # (a) System member credentials (b) Slice credentials (c) project credentials
        #

        #For compatability with OMNI which passes urn str list instead of dict for members_to_remove
        if 'members_to_remove' in options and type(options['members_to_remove'][0]) is str:
            for i in range(0, len(options['members_to_remove'])):
                options['members_to_remove'][i] = {'SLICE_MEMBER': options['members_to_remove'][i]}

        for option_key, option_value in options.iteritems():
            if option_key in ['members_to_add', 'members_to_change']:
                for member_dict in option_value:
                    # LEAD membership can be changed by LEAD himself or by ROOT
                    if member_dict['SLICE_MEMBER'] == slice_lead and (user_urn_from_cert != slice_lead or user_urn_from_cert != target_urn_from_cred):
                        raise self.gfed_ex.GFedv2ArgumentError("Only slice LEAD or ROOT can modify lead membership "+ str(urn))

                    member_cert = member_dict['MEMBER_CERTIFICATE'] if 'MEMBER_CERTIFICATE' in member_dict else self._get_member_certificate(member_dict['SLICE_MEMBER'])
                    member_role = member_dict['SLICE_ROLE'] if 'SLICE_ROLE' in member_dict else 'MEMBER'
                    member_pri = self._delegate_tools.get_default_privilege_list(role_=member_role, context_='SLICE')
                    if 'EXTRA_PRIVILEGES' in member_dict:
                        member_pri = member_pri+member_dict['EXTRA_PRIVILEGES']
                        member_dict.pop('EXTRA_PRIVILEGES', None)
                    member_dict['SLICE_CREDENTIALS'] = geniutil.create_credential_ex(owner_cert=member_cert, target_cert=slice_cert,
                                                                                     issuer_key=self._sa_pr, issuer_cert=self._sa_c,
                                                                                     privileges_list=member_pri, expiration=self.CRED_EXPIRY)
                    member_dict['SLICE_CERTIFICATE'] = slice_cert
                    if member_role == 'LEAD':
                        slice_lookup_result[0]['SLICE_LEAD'] = member_dict['SLICE_MEMBER']
                        self._resource_manager_tools.object_update(self.AUTHORITY_NAME, slice_lookup_result[0], 'slice', {'SLICE_URN':urn})

            elif option_key == 'members_to_remove':
                for member_dict in option_value:
                    if slice_lead == member_dict['SLICE_MEMBER']:
                        raise self.gfed_ex.GFedv2ArgumentError("The specified user is slice LEAD and therefore cannot be removed "+ str(urn))
        return self._resource_manager_tools.member_modify(self.AUTHORITY_NAME, 'slice_member', urn, options, 'SLICE_MEMBER', 'SLICE_URN')

    def _get_member_certificate(self, member_urn):
        """
        Helper function to retrieve user certificate from MA database
        :param member_urn:
        :return:
        """
        _member_authority_resource_manager = pm.getService('omemberauthorityrm')
        lookup_results = _member_authority_resource_manager.lookup_member(credentials=None, match={'MEMBER_URN':member_urn}, filter_=[], options=None)
        if lookup_results:
            return lookup_results[0]['MEMBER_CERTIFICATE']
        else:
            raise self.gfed_ex.GFedv2ArgumentError("The specified user does not exist"+ str(member_urn))

    def _update_cred_expiry(self, cred, obj_cert, expiry):
        """
        Helper function to update expiry of credentials
        :param cred:
        :param obj_cert:
        :param expiry:
        :return:
        """
        geniutil = pm.getService('geniutil')
        owner_cert = geniutil.extract_owner_certificate(cred)
        priv, _ = geniutil.get_privileges_and_target_urn(cred)
        return geniutil.create_credential_ex(owner_cert=owner_cert, target_cert=obj_cert,
                                             issuer_key=self._sa_pr, issuer_cert=self._sa_c,
                                             privileges_list=priv, expiration=expiry)


    def modify_project_membership(self, urn, credentials, options):
        """
        Modify a project membership object.
        """
        #<UT>
        project_lookup_result = self.lookup_project(None, match={'PROJECT_URN':urn}, filter_=[], options=None)

        if not len(project_lookup_result):
            raise self.gfed_ex.GFedv2ArgumentError("The specified project does not exist: "+ str(urn))

        if len(project_lookup_result) > 1:
            raise self.gfed_ex.GFedv2DuplicateError("There are more than one instance of specified project: "+ str(urn))

        project_cert = project_lookup_result[0]['PROJECT_CERTIFICATE']
        project_lead = project_lookup_result[0]['PROJECT_LEAD']
        geniutil = pm.getService('geniutil')
        owner_cert = geniutil.extract_owner_certificate(credentials)
        user_urn_from_cert, _, _ = geniutil.extract_certificate_info(owner_cert)
        _, target_urn_from_cred = geniutil.get_privileges_and_target_urn(credentials)


        for option_key, option_value in options.iteritems():
            if option_key in ['members_to_add', 'members_to_change']:
                for member_dict in option_value:
                    # LEAD membership can be changed by LEAD himself or by ROOT
                    if member_dict['PROJECT_MEMBER'] == project_lead and ( user_urn_from_cert != project_lead or user_urn_from_cert != target_urn_from_cred):
                        raise self.gfed_ex.GFedv2ArgumentError("Only project LEAD or ROOT can modify lead membership "+ str(urn))

                    member_cert = member_dict['MEMBER_CERTIFICATE']
                    member_role = member_dict['PROJECT_ROLE'] if 'PROJECT_ROLE' in member_dict else 'MEMBER'
                    member_pri = self._delegate_tools.get_default_privilege_list(role_=member_role, context_='PROJECT')
                    if 'EXTRA_PRIVILEGES' in member_dict:
                        member_pri = member_pri+member_dict['EXTRA_PRIVILEGES']
                        member_dict.pop('EXTRA_PRIVILEGES', None)
                    member_dict['PROJECT_CREDENTIALS'] = geniutil.create_credential_ex(owner_cert=member_cert, target_cert=project_cert,
                                                                                       issuer_key=self._sa_pr, issuer_cert=self._sa_c,
                                                                                       privileges_list=member_pri, expiration=self.CRED_EXPIRY)
                    _, member_uuid_int, _ = geniutil.extract_certificate_info(member_cert)
                    member_uuid = uuid.UUID(int=member_uuid_int).urn[9:]

                    member_dict['PROJECT_MEMBER_UID'] = str(member_uuid)
                    member_dict['PROJECT_CERTIFICATE'] = project_cert
                    if member_role == 'LEAD':
                        project_lookup_result[0]['PROJECT_LEAD'] = member_dict['PROJECT_MEMBER']
                        self._resource_manager_tools.object_update(self.AUTHORITY_NAME, project_lookup_result[0], 'project', {'PROJECT_URN':urn})

            elif option_key == 'members_to_remove':
                for member_dict in option_value:
                    if project_lead == member_dict['PROJECT_MEMBER']:
                        raise self.gfed_ex.GFedv2ArgumentError("The specified user is project LEAD and therefore cannot be removed "+ str(urn))

        return self._resource_manager_tools.member_modify(self.AUTHORITY_NAME, 'project_member', urn, options, 'PROJECT_MEMBER', 'PROJECT_URN')

    def update_slice_credentials_for_member(self, member_urn, credentials, options):
        """
        updates slice credentials after member certificate update due to membership renewal or revocation
        """
        member_cert = options['MEMBER_CERTIFICATE']

        slice_memberships = self.lookup_slice_membership_for_member(member_urn, credentials, None)
        geniutil = pm.getService('geniutil')

        for membership in slice_memberships:
            slice_cert = membership['SLICE_CERTIFICATE']
            slice_creds_old = membership['SLICE_CREDENTIALS']
            slice_prvlg, slice_urn = geniutil.get_privileges_and_target_urn(slice_creds_old)
            slice_exp = geniutil.get_expiration(slice_creds_old)
            slice_creds_new = geniutil.create_credential_ex(owner_cert=member_cert, target_cert=slice_cert,
                                                            issuer_key=self._sa_pr, issuer_cert=self._sa_c,
                                                            privileges_list=slice_prvlg, expiration=slice_exp)

            update_data = {'members_to_change': [{'SLICE_CREDENTIALS': slice_creds_new}]}
            self._resource_manager_tools.member_modify(self.AUTHORITY_NAME, 'slice_member', slice_urn,
                                                       update_data, 'SLICE_MEMBER', 'SLICE_URN')

    def update_project_credentials_for_member(self, member_urn, credentials, options):
        """
        updates project credentials after member certificate update due to membership renewal or revocation
        """
        member_cert = options['MEMBER_CERTIFICATE']
        project_memberships = self.lookup_project_membership_for_member(member_urn, credentials, None)
        geniutil = pm.getService('geniutil')

        for membership in project_memberships:
            project_cert = membership['PROJECT_CERTIFICATE']
            project_creds_old = membership['PROJECT_CREDENTIALS']
            project_prvlg, project_urn = geniutil.get_privileges_and_target_urn([{'geni_type': 'geni_sfa', 'geni_version':'3', 'geni_value': project_creds_old}])
            project_exp = geniutil.get_expiration(project_creds_old)
            project_creds_new = geniutil.create_credential_ex(owner_cert=member_cert, target_cert=project_cert,
                                                              issuer_key=self._sa_pr, issuer_cert=self._sa_c,
                                                              privileges_list=project_prvlg, expiration=project_exp)

            update_data = {'members_to_change': [{'PROJECT_CREDENTIALS': project_creds_new}]}
            self._resource_manager_tools.member_modify(self.AUTHORITY_NAME, 'project_member', project_urn,
                                                       update_data, 'PROJECT_MEMBER', 'PROJECT_URN')

    def lookup_slice_membership(self, urn, credentials, match, filter_, options):
        """
        Lookup a slice membership object.
        """
        return self._resource_manager_tools.member_lookup(self.AUTHORITY_NAME, 'slice_member', 'SLICE_URN', urn, ['SLICE_URN'], match, filter_)

    def lookup_project_membership(self, urn, credentials, match, filter_, options):
        """
        Lookup a project membership object.
        """

        return self._resource_manager_tools.member_lookup(self.AUTHORITY_NAME, 'project_member', 'PROJECT_URN', urn, ['PROJECT_URN'], match, filter_)

    def lookup_slice_membership_for_member(self, member_urn, credentials, options):
        """
        Lookup a slice membership object for a given member.
        """
        return self._resource_manager_tools.member_lookup(self.AUTHORITY_NAME, 'slice_member', 'SLICE_MEMBER', member_urn, ['SLICE_MEMBER'], {}, {})

    def lookup_project_membership_for_member(self, member_urn, credentials, options):
        """
        Lookup a project membership object for a given member.
        """
        return self._resource_manager_tools.member_lookup(self.AUTHORITY_NAME, 'project_member', 'PROJECT_MEMBER', member_urn, ['PROJECT_MEMBER'], {}, {})

    def get_credentials(self, slice_urn, member_urn, options):
        """

        :param slice_urn:
        :param member_urn:
        :param options:
        :return:
        """
        lookup_results = self._resource_manager_tools.member_lookup(self.AUTHORITY_NAME, 'slice_member', 'SLICE_URN', slice_urn, ['SLICE_URN'], {'SLICE_MEMBER': member_urn}, {})
        if not lookup_results:
            raise self.gfed_ex.GFedv2ArgumentError("The specified slice does not exist "+ str(slice_urn))

        return [{'geni_type': 'geni_sfa', 'geni_version':'3', 'geni_value': lookup_results[0]['SLICE_CREDENTIALS']}]
