import eisoil.core.pluginmanager as pm
import eisoil.core.log
import pyrfc3339
import copy

logger=eisoil.core.log.getLogger('ofed')

GSAv2DelegateBase = pm.getService('gsav2delegatebase')
gfed_ex = pm.getService('apiexceptionsv2')
VERSION = '2'

class OSAv2Delegate(GSAv2DelegateBase):
    """
    Implements Slice Authority methods.

    Does validity checking on passed options.
    """

    def __init__(self):
        """
        Get plugins for use in other class methods.

        Retrieve whitelists for use in validity checking.
        """
        self._slice_authority_resource_manager = pm.getService('osliceauthorityrm')
        self._delegate_tools = pm.getService('delegatetools')
        self._api_tools = pm.getService('apitools')
        self._logging_authority_resource_manager = pm.getService('ologgingauthorityrm')
        self._slice_whitelist = self._delegate_tools.get_whitelist('SLICE')
        self._sliver_info_whitelist = self._delegate_tools.get_whitelist('SLIVER_INFO')
        self._project_whitelist = self._delegate_tools.get_whitelist('PROJECT')
        self._gsav2handler = pm.getService('gsav2handler')

    def get_version(self):
        """
        Get implementation details from resource manager. Supplement these with
        additional details specific to the delegate.
        """
        version = self._delegate_tools.get_version(self._slice_authority_resource_manager)
        version['VERSION'] = VERSION
        version['FIELDS'] = self._delegate_tools.get_supplementary_fields(['SLICE', 'SLIVER', 'PROJECT'])
        version['ROLES'] = self._slice_authority_resource_manager.roles()
        return version

    def create(self, type_, credentials, fields, options):
        """
        Depending on the object type defined in the request, check the validity
        of passed fields for a 'create' call; if valid, create this object using
        the resource manager.
        """
        fields_copy = copy.copy(fields) if fields else None
        options_copy = copy.copy(options) if options else None
        client_ssl_cert = self._gsav2handler.requestCertificate()

        if (type_.upper()=='SLICE'):
            self._delegate_tools.object_creation_check(fields, self._slice_whitelist)
            self._delegate_tools.object_consistency_check(type_, fields)
            self._delegate_tools.slice_name_check(fields.get('SLICE_NAME')) # Specific check for slice name restrictions
            self._delegate_tools.check_if_authorized(credentials, client_ssl_cert, 'CREATE', 'SLICE', fields=fields)
            ret_values = self._slice_authority_resource_manager.create_slice(credentials, fields, options)
            self._logging_authority_resource_manager.append_event_log(authority='sa', method='create', target_type=type_.upper(),
                    fields=fields_copy, options= options_copy, credentials=ret_values['SLICE_CREDENTIALS'])
            return ret_values
        elif (type_.upper()=='SLIVER_INFO'):
            self._delegate_tools.object_creation_check(fields, self._sliver_info_whitelist)
            self._delegate_tools.object_consistency_check(type_, fields)
            self._delegate_tools.check_if_authorized(credentials, client_ssl_cert, 'CREATE', 'SLIVER_INFO', fields=fields)
            return self._slice_authority_resource_manager.create_sliver_info(credentials, fields, options)
        elif (type_.upper()=='PROJECT'):
            self._delegate_tools.object_creation_check(fields, self._project_whitelist)
            self._delegate_tools.object_consistency_check(type_, fields)
            self._delegate_tools.project_name_check(fields.get('PROJECT_NAME')) # Specific check for slice name restrictions
            self._delegate_tools.check_if_authorized(credentials, client_ssl_cert, 'CREATE', 'PROJECT')
            ret_values =  self._slice_authority_resource_manager.create_project(credentials, fields, options)
            self._logging_authority_resource_manager.append_event_log(authority='sa', method='create', target_type=type_.upper(),
                    fields=fields_copy, options= options_copy, certificate=client_ssl_cert, target_urn=ret_values['PROJECT_URN'])
            return ret_values

        else:
            raise gfed_ex.GFedv2NotImplementedError("No create method found for object type: " + str(type_))

    def update(self, type_, urn, credentials, fields, options):
        """
        Depending on the object type defined in the request, check the validity
        of passed fields for a 'update' call; if valid, update this object using
        the resource manager.
        """
        fields_copy = copy.copy(fields) if fields else None
        options_copy = copy.copy(options) if options else None
        client_ssl_cert = self._gsav2handler.requestCertificate()

        if (type_.upper() == 'SLICE'):
            self._delegate_tools.check_if_authorized(credentials, client_ssl_cert, 'UPDATE', 'SLICE', target_urn=urn)

            if 'SLICE_EXPIRATION' in fields:
                try:
                    pyrfc3339.parse(fields.get('SLICE_EXPIRATION'))
                except Exception as e:
                    try:
                        pyrfc3339.parse(fields.get('SLICE_EXPIRATION')+'Z')
                        fields['SLICE_EXPIRATION'] = fields.get('SLICE_EXPIRATION')+'Z'
                    except Exception as e:
                        raise gfed_ex.GFedv2ArgumentError('Expiration time format is not supported')

                update_expiration_time = fields.get('SLICE_EXPIRATION')
                lookup_result = self._slice_authority_resource_manager.lookup_slice(credentials,
                                                                                    {'SLICE_URN' : str(urn)}, [], {})
                if lookup_result:
                    # keyed_lookup_result enables referencing an dictionary with any chosen key_name. For example,
                    # SLICE_URN can be used as the key for the dictionary return when looking up a slice.
                    # This is needed here to enable fetching out the SLICE_CREATION time belonging to a certain SLICE_URN
                    keyed_lookup_result = self._delegate_tools.to_keyed_dict(lookup_result, "SLICE_URN")
                    is_valid = self._delegate_tools.validate_expiration_time(str(keyed_lookup_result[urn]['SLICE_EXPIRATION']),
                                                                                update_expiration_time, type_)
                    if not is_valid:
                        raise gfed_ex.GFedv2ArgumentError("Slice Expiration can only be extended, never reduced. Current Expiration: "+str(keyed_lookup_result[urn]['SLICE_EXPIRATION']))
                else:
                    raise gfed_ex.GFedv2ArgumentError("Specified slice object does not exist: " + urn)

            # Consistency check
            self._delegate_tools.object_update_check(fields, self._slice_whitelist)
            self._delegate_tools.object_consistency_check(type_, fields)

            # Update
            ret_values = self._slice_authority_resource_manager.update_slice(urn, credentials, fields, options)

            # Logging
            self._logging_authority_resource_manager.append_event_log(authority='sa', method='update', target_type=type_.upper(),
                    fields=fields_copy, options= options_copy, target_urn=urn, credentials=credentials)
            return ret_values

        elif (type_.upper()=='SLIVER_INFO'):
            self._delegate_tools.object_update_check(fields, self._sliver_info_whitelist)
            self._delegate_tools.object_consistency_check(type_, fields)
            return self._slice_authority_resource_manager.update_sliver_info(urn, credentials, fields, options)
        elif (type_.upper()=='PROJECT'):
            self._delegate_tools.check_if_authorized(credentials, client_ssl_cert, 'UPDATE', 'PROJECT', target_urn=urn)
            update_expiration_time = fields.get('PROJECT_EXPIRATION')
            if update_expiration_time:
                lookup_result = self._slice_authority_resource_manager.lookup_project(credentials,
                                                                                     {'PROJECT_URN' : str(urn)}, [], {})

                # keyed_lookup_result enables referencing an dicitionary with any chosen key_name. For example,
                # SLICE_URN can be used as the key for the dictionary return when looking up a slice.
                # This is needed here to enable fetching out the SLICE_CREATION time belonging to a certain SLICE_URN
                keyed_lookup_result = self._delegate_tools.to_keyed_dict(lookup_result, "PROJECT_URN")
                is_valid = self._delegate_tools.validate_expiration_time(str(keyed_lookup_result[urn]['PROJECT_EXPIRATION']),
                                                                        update_expiration_time)

                if not is_valid:
                    raise gfed_ex.GFedv2ArgumentError("Project Expiration can only be extended, never reduced. Current Expiration: "+str(keyed_lookup_result[urn]['PROJECT_EXPIRATION']))

            self._delegate_tools.object_update_check(fields, self._project_whitelist)
            self._delegate_tools.object_consistency_check(type_, fields)
            ret_values = self._slice_authority_resource_manager.update_project(urn, credentials, fields, options)
            self._logging_authority_resource_manager.append_event_log(authority='sa', method='update', target_type=type_.upper(),
                    fields=fields_copy, options= options_copy, target_urn=urn, credentials=credentials)
            return ret_values

        else:
            raise gfed_ex.GFedv2NotImplementedError("No update method found for object type: " + str(type_))

    def delete(self, type_, urn, credentials, options):
        """
        Depending on the object type defined in the request, delete this object
        using the resource manager.
        """
        options_copy = copy.copy(options) if options else None
        client_ssl_cert = self._gsav2handler.requestCertificate()

        if type_.upper()=='SLICE':
            raise gfed_ex.GFedv2NotImplementedError("No authoritative way to know that there aren't live slivers associated with a slice.")
        elif type_.upper()=='SLIVER_INFO':
            return self._slice_authority_resource_manager.delete_sliver_info(urn,  credentials, options)
        elif type_.upper()=='PROJECT':

            self._delegate_tools.check_if_authorized(credentials, client_ssl_cert, 'DELETE', 'PROJECT', target_urn=urn)
            ret_values = self._slice_authority_resource_manager.delete_project(urn, credentials,  options)
            self._logging_authority_resource_manager.append_event_log(authority='sa', method='delete', target_type=type_.upper(),
                    fields=None, options= options_copy, target_urn=urn, credentials=credentials)
            return ret_values

        else:
            raise gfed_ex.GFedv2NotImplementedError("No delete method found for object type: " + str(type_))

    def lookup(self, type_, credentials, match, filter_, options):
        """
        Depending on the object type defined in the request, lookup this object
        using the resource manager.
        """
        # Turn off logging for lookups
        # options_copy = copy.copy(options) if options else None

        if type_.upper() == 'SLICE':
            # Consistency check
            self._delegate_tools.object_lookup_check(match, self._slice_whitelist)
            self._delegate_tools.object_consistency_check(type_, match)

            # Temporarily lookup call are not authorized
            # self._delegate_tools.check_if_authorized(credentials, 'LOOKUP', 'SLICE')

            remove_anchor_key = False
            if filter_ and 'SLICE_URN' not in filter_:
                filter_.append('SLICE_URN')
                remove_anchor_key = True

            match_urn_list = self._delegate_tools.decompose_urns(match, 'SLICE_URN')

            result_list = []
            for urn in match_urn_list:
                # Compatability issue with OMNI which passes 'f' as its value. However CBAS stores it as bool
                if 'SLICE_EXPIRED' in urn:
                    urn.pop('SLICE_EXPIRED')
                result_list = result_list + self._slice_authority_resource_manager.lookup_slice(credentials, urn, [] if filter_ is None else filter_, options)

            # self._logging_authority_resource_manager.append_event_log(authority='sa', method='lookup',
            #  target_type=type_.upper(), fields=None, options= options_copy, target_urn=match, credentials=credentials)

            return self._delegate_tools.to_keyed_dict(result_list, "SLICE_URN", filter_, remove_anchor_key)

        elif type_.upper() == 'SLIVER_INFO':
            # Consistency check
            self._delegate_tools.object_lookup_check(match, self._sliver_info_whitelist)
            self._delegate_tools.object_consistency_check(type_, match)

            remove_anchor_key = False
            if filter_ and 'SLIVER_INFO_URN' not in filter_:
                filter_.append('SLIVER_INFO_URN')
                remove_anchor_key = True

            return self._delegate_tools.to_keyed_dict(self._slice_authority_resource_manager.lookup_sliver_info(
                credentials, match, [] if filter_ is None else filter_, options), "SLIVER_INFO_URN", filter_, remove_anchor_key)

        elif type_.upper() == 'PROJECT':
            # self._delegate_tools.check_if_authorized(credentials, 'LOOKUP', 'PROJECT')

            # Consistency check
            self._delegate_tools.object_lookup_check(match, self._project_whitelist)
            self._delegate_tools.object_consistency_check(type_, match)

            remove_anchor_key = False
            if filter_ and 'PROJECT_URN' not in filter_:
                filter_.append('PROJECT_URN')
                remove_anchor_key = True

            ret_values = self._slice_authority_resource_manager.lookup_project(credentials, match, [] if filter_ is None else filter_, options)
            # self._logging_authority_resource_manager.append_event_log(authority='sa', method='lookup', target_type=type_.upper(),
            #         fields=None, options= options_copy, target_urn=match, credentials=credentials)
            return self._delegate_tools.to_keyed_dict(ret_values, "PROJECT_URN", filter_, remove_anchor_key)
        else:
            raise gfed_ex.GFedv2NotImplementedError("No lookup method found for object type: " + str(type_))

        # ---- Slice Member Service Methods and Project Member Service Methods
    def modify_membership(self, type_, urn, credentials, options):
        """
        # Modify object membership, adding, removing and changing roles of members
        #    with respect to given object
        #
        # Arguments:
        #   type: type of object for whom to lookup membership (
        #       in the case of Slice Member Service, "SLICE",
        #       in the case of Project Member Service, "PROJECT")
        #   urn: URN of slice/project for which to modify membership
        #   Options:
        #       members_to_add: List of member_urn/role tuples for members to add to
        #              slice/project of form
        #                 {'SLICE_MEMBER' : member_urn, 'SLICE_ROLE' : role}
        #                    (or 'PROJECT_MEMBER/PROJECT_ROLE
        #                    for Project Member Service)
        #       members_to_remove: List of member_urn of members to
        #                remove from slice/project
        #       members_to_change: List of member_urn/role tuples for
        #                 members whose role
        #                should change as specified for given slice/project of form
        #                {'SLICE_MEMBER' : member_urn, 'SLICE_ROLE' : role}
        #                (or 'PROJECT_MEMBER/PROJECT_ROLE for Project Member Service)
        #
        # Return:
        #   None
        """
        options_copy = copy.deepcopy(options) if options else None
        client_ssl_cert = self._gsav2handler.requestCertificate()

        if (type_.upper()=='SLICE'):
            self._delegate_tools.check_if_authorized(credentials, client_ssl_cert, 'UPDATE', 'SLICE_MEMBER', urn)
            #self._delegate_tools.check_if_modify_membership_authorized(credentials, options, type, urn_)
            self._delegate_tools.member_check(['SLICE_MEMBER', 'SLICE_ROLE', 'MEMBER_CERTIFICATE', 'EXTRA_PRIVILEGES'], options)
            self._slice_authority_resource_manager.modify_slice_membership(urn, credentials, options)
            self._logging_authority_resource_manager.append_event_log(authority='sa', method='modify_membership', target_type=type_.upper(),
                    fields=None, options= options_copy, target_urn=urn, credentials=credentials)

        elif (type_.upper()=='PROJECT'):
            self._delegate_tools.check_if_authorized(credentials, client_ssl_cert, 'UPDATE', 'PROJECT_MEMBER', urn)
            self._delegate_tools.check_if_modify_membership_authorized(credentials, options, type_, urn)
            self._delegate_tools.member_check(['PROJECT_MEMBER', 'PROJECT_ROLE', 'MEMBER_CERTIFICATE', 'EXTRA_PRIVILEGES'], options)
            self._slice_authority_resource_manager.modify_project_membership(urn, credentials, options)

            self._logging_authority_resource_manager.append_event_log(authority='sa', method='modify_membership', target_type=type_.upper(),
                    fields=None, options= options_copy, target_urn=urn, credentials=credentials)

        else:
            raise gfed_ex.GFedv2NotImplementedError("No membership modification method found for object type: " + str(type_))

    def lookup_members(self, type_, urn, credentials, match, filter_, options):
        """
        # Lookup members of given object and their roles within that object
        #
        # Arguments:
        #   type: type of object for whom to lookup membership
        #          (in the case of Slice Member Service, "SLICE",
        #           in the case of Project Member Service, "PROJECT")
        #   urn: URN of object for which to provide current members and roles
        #
        # Return:
        #    List of dictionaries of member_urn/role pairs
        #       [{'SLICE_MEMBER': member_urn,
        #        'SLICE_ROLE': role }...]
        #         (or PROJECT_MEMBER/PROJECT_ROLE
        #          for Project Member Service)
        #          where 'role' is a string of the role name.
        """
        # options_copy = list(options) if options else None

        if (type_.upper()=='SLICE'):
            #self._delegate_tools.check_if_authorized(credentials, 'LOOKUP', 'SLICE_MEMBER', target_urn=urn)
            if 'SLICE_EXPIRED' in match: # Compatabilty issue with OMNI. CBAS does not store SLICE_EXPIRED in slice creds
                match.pop('SLICE_EXPIRED')
            filter_ = ['SLICE_MEMBER', 'SLICE_ROLE']
            ret_values = self._slice_authority_resource_manager.lookup_slice_membership(urn, credentials, match, filter_ , options)
            # self._logging_authority_resource_manager.append_event_log(authority='sa', method='lookup_members', target_type=type_.upper(),
            #         fields=None, options= options_copy, target_urn=urn, credentials=credentials)
            return ret_values

        elif (type_.upper()=='PROJECT'):
            #self._delegate_tools.check_if_authorized(credentials, 'LOOKUP', 'PROJECT_MEMBER', target_urn=urn)
            if 'PROJECT_EXPIRED' in match: # Compatabilty issue with OMNI. CBAS does not store PROJECT_EXPIRED in project creds
                match.pop('PROJECT_EXPIRED')
            filter_ = ['PROJECT_MEMBER', 'PROJECT_ROLE']
            ret_values = self._slice_authority_resource_manager.lookup_project_membership(urn, credentials, match, filter_, options)
            # self._logging_authority_resource_manager.append_event_log(authority='sa', method='lookup_members', target_type=type_.upper(),
            #         fields=None, options= options_copy, target_urn=urn, credentials=credentials)
            return ret_values
        else:
            raise gfed_ex.GFedv2NotImplementedError("No member lookup method found for object type: " + str(type_))

    def lookup_for_member(self, type_, member_urn, credentials, options, match={}, filter_=[]):
        """
        # Lookup objects of given type for which the given member belongs
        #
        # Arguments:
        #   type: type of object for whom to lookup membership
        #          (in the case of Slice Member Service, "SLICE",
        #           in the case of Project Member Service, "PROJECT")
        #   member_urn: The member for whom to find slices to which it belongs
        #
        # Return:
        #    List of dictionary of urn/role pairs
        #        [('SLICE_URN' : slice_urn, 'SLICE_ROLE' : role} ...]
        #        (or PROJECT_MEMBER/PROJECT_ROLE
        #           for Project Member Service)
        #        for each object to which a member belongs,
        #        where role is a string of the role name
        """
        # Turn off logging for lookups
        # options_copy = list(options) if options else None

        if (type_.upper()=='SLICE'):
            filter_ = ['SLICE_URN', 'SLICE_ROLE']
            ret_values = self._slice_authority_resource_manager.lookup_slice_membership_for_member(member_urn, credentials, options, match, filter_)
            # self._logging_authority_resource_manager.append_event_log(authority='sa', method='lookup_for_member', target_type=type_.upper(),
            #         fields=None, options= options_copy, target_urn=member_urn, credentials=credentials)
            return ret_values

        elif (type_.upper()=='PROJECT'):
            filter_ = ['PROJECT_URN', 'PROJECT_ROLE']
            ret_values = self._slice_authority_resource_manager.\
                lookup_project_membership_for_member(member_urn, credentials, options, match, filter_)
            # self._logging_authority_resource_manager.append_event_log(authority='sa', method='lookup_for_member', target_type=type_.upper(),
            #         fields=None, options= options_copy, target_urn=member_urn, credentials=credentials)
            return ret_values
        else:
            raise gfed_ex.GFedv2NotImplementedError("No lookup for member method found for object type: " + str(type_))

    def verify_credentials(self, creds_to_verify, target_urn, credentials):
        """
        Verifies if given credentials are valid and trusted
        """
        client_ssl_cert = self._gsav2handler.requestCertificate()
        return self._delegate_tools.verify_credentials(creds_to_verify, client_ssl_cert, target_urn)

    def delegate_credentials(self, delagetee_cert, issuer_key, privileges_list, expiration,
                             delegatable, credentials):
        """
        Generates delegate credentials
        """
        client_ssl_cert = self._gsav2handler.requestCertificate()
        ret_values = self._delegate_tools.delegate_credentials(delagetee_cert, client_ssl_cert, issuer_key, privileges_list,
                                                         expiration, delegatable, credentials)
        #Logging of the action
        geniutil = pm.getService('geniutil')
        delegatee_urn,_,_ = geniutil.extract_certificate_info(delagetee_cert)
        self._logging_authority_resource_manager.append_event_log(authority='sa', method='delegate_credentials', target_type='SLICE',
                    fields={'Delegatee URN':delegatee_urn}, options= {'Privileges':privileges_list}, credentials=credentials)
        return ret_values

    def update_credentials_for_member(self, member_urn, credentials, options):
        """
        updates project and slice credentials after member certificate update due to membership renewal or revocation
        :param member_urn:
        :param credentials:
        :return:
        """
        self._slice_authority_resource_manager.\
                update_slice_credentials_for_member(member_urn, credentials, options)
        self._slice_authority_resource_manager.\
                update_project_credentials_for_member(member_urn, credentials, options)

    def get_credentials(self, slice_urn, credentials, options):
        """

        :param slice_urn:
        :param credentials:
        :param options:
        :return:
        """
        client_ssl_cert = self._gsav2handler.requestCertificate()
        self._delegate_tools.verify_credentials(credentials, client_ssl_cert)
        geniutil = pm.getService('geniutil')
        owner_cert = geniutil.extract_owner_certificate(credentials)
        member_urn, _, _ = geniutil.extract_certificate_info(owner_cert)
        return self._slice_authority_resource_manager.get_credentials(slice_urn, member_urn, options)
