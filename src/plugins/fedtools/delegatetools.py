from eisoil.core import serviceinterface
from eisoil.config import expand_eisoil_path
import eisoil.core.pluginmanager as pm
import eisoil.core.log

from delegateexceptions import *
from apiexceptionsv2 import *


import os.path
import json
import uuid
import pyrfc3339, datetime, pytz
import re

logger = eisoil.core.log.getLogger('delegatetools')

class DelegateTools(object):
    """
    Common tools used to implement a ClearingHouse (CH) delegate.
    """

    JSON_COMMENT = "__comment" #: delimeter for comments in loaded JSON files (config.json and defaults.json)
    REQUIRED_METHOD_KEYS = ['members_to_add', 'members_to_change', 'members_to_remove'] #: list of valid keys to be passed as 'options' in a 'modify_membership' call
    GET_VERSION_FIELDS = ['URN', 'IMPLEMENTATION', 'SERVICES', 'CREDENTIAL_TYPES', 'ROLES', 'SERVICE_TYPES', 'API_VERSIONS'] #: list of fields possible in a 'get_version' API call response

    def __init__(self):
        """
        Load configuration files. Combine the default field names with the supplemenary fields to form a combined list.
        """
        self.STATIC = {} #: holds static configuration and settings loaded from JSON files (config.json and defaults.json)
        self._load_files()
        self._combine_fields()

        config = pm.getService("config")
        self.TRUSTED_CERT_PATH = expand_eisoil_path(config.get("delegatetools.trusted_cert_path")) +'/' #<UT>
        self.TRUSTED_CRL_PATH = expand_eisoil_path(config.get("delegatetools.trusted_crl_path")) + '/' #<UT>

    def _load_files(self):
        """
        Load JSON configuration and default files.

        Raises:
            MalformedConfigFile: An error occured when loading the JSON file.

        """
        paths = self._get_paths()
        for path_key, path_value in paths.iteritems():
            if not os.path.exists(path_value):
                raise ConfigFileMissing(path_value)
            try:
                self.STATIC[path_key] = self._strip_comments(json.load(open(path_value)))
            except Exception:
                raise MalformedConfigFile(path_value, '')

    def _combine_fields(self):
        """
        Combine default fields with supplementary fields to form a combined set.

        Supplementary fields can also overwrite exsiting default fields.

        """
        self.STATIC['COMBINED'] = self.STATIC['DEFAULTS']
        for type_key, type_value in self.STATIC['SUPPLEMENTARY_FIELDS'].iteritems():
            if type_key not in DelegateTools.JSON_COMMENT:
                for field_key, field_value in type_value.iteritems():
                    self.STATIC['COMBINED'][type_key.upper()][field_key.upper()] = field_value

    def _strip_comments(self, json):
        """
        Recursively strip comments out of loaded JSON files.

        The delimiter used to define a comment is defined in a global variable (JSON_COMMENT).

        Args:
            json: JSON content to strip comments from

        Returns:
            JSON content with comments removed

        """
        if type(json) in [str, unicode, int, float, bool, type(None)]:
            return json
        if isinstance(json, list):
            return [self._strip_comments(j) for j in json if not ((type(j) in [str, unicode]) and j.startswith(DelegateTools.JSON_COMMENT))]
        if isinstance(json, dict):
            return dict( (k, self._strip_comments(v)) for (k,v) in json.iteritems() if k != DelegateTools.JSON_COMMENT) # there would be a dict comprehension from 2.7

    def _get_paths(self):

        """
        Get full file paths for JSON files to load (config.json and defaults.json).

        Returns:
            dictionary containing the loaded JSON content
        """

        config = pm.getService("config")
        config_path = config.get("delegatetools.config_path")
        supplemetary_fields_path = config.get("delegatetools.supplemetary_fileds_path")
        service_registry_path = config.get("delegatetools.service_registry_path")
        defaults_path = config.get("delegatetools.defaults_path")
        authz_path = config.get("delegatetools.authz_path") #<UT>
        roles_path = config.get("delegatetools.roles_path") #<UT>
        return {'CONFIG' : expand_eisoil_path(config_path),
                'DEFAULTS' : expand_eisoil_path(defaults_path),
                'SUPPLEMENTARY_FIELDS' : expand_eisoil_path(supplemetary_fields_path),
                'REGISTRY' : expand_eisoil_path(service_registry_path),
                'AUTHZ' : expand_eisoil_path(authz_path), #<UT>
                'ROLES' : expand_eisoil_path(roles_path), #<UT>
                }


    @serviceinterface
    def validate_expiration_time(self, original_value, value_in_question, type_=None):
        """
        Validate the expiration time value passed to Update or Create Methods.

        Args:
            original_value: The original value that needs to be compared (e.g., SLICE creation date)
            value_in_question: The value that is doubted for correctness (e.g., Expiry time update date)

        Returns:
            a boolean value to indicate whether the expiration time valid or not
        """
        parsed_original_value = pyrfc3339.parse(original_value)
        parsed_value_in_question = pyrfc3339.parse(value_in_question)
        now = pytz.timezone("UTC").localize(datetime.datetime.utcnow())

        # Check if the object has already expired
        if now > parsed_original_value:
            raise GFedv2ArgumentError("Update is not possible because the object has already expired.")

        if type_:
            maximum_expansion_duration = self.STATIC['CONFIG'][type_]['max_%s_extension_time' %type_.lower()]
            configuration_delta = datetime.timedelta(days=maximum_expansion_duration)
            delta_time_days =  parsed_value_in_question - parsed_original_value
            return True if parsed_original_value < parsed_value_in_question and delta_time_days < configuration_delta  else False
        else:
            return parsed_original_value < parsed_value_in_question

    @serviceinterface
    def get_fields(self, type_):
        """
        Get combined fields for a given object type.

        Args:
            type_: the type of object

        Returns:
            the combined fields

        """
        return self.STATIC['COMBINED'][type_]

    @serviceinterface
    def get_supplementary_fields(self, types):
        """
        Get supplementary fields for a set of given object types.

        Args:
            types: a list of object types

        Returns:
            the supplementary fields

        """
        result = {}
        for _type in types:
            try:
                result.update(self.STATIC['SUPPLEMENTARY_FIELDS'][_type])
            except KeyError:
                pass
        return result

    @serviceinterface
    def get_config(self, type_):
        """
        Get configuration fields for a given object type.

        Args:
            type_: the type of object

        Returns:
            the configuration fields

        """
        return self.STATIC['CONFIG'].get(type_, {})

    @serviceinterface
    def get_registry(self):
        """
        Get REGISTRY fields for a given object type.

        Args:
            type_: the type of object

        Returns:
            the REGISTRY fields
        """
        return self.STATIC['REGISTRY']

    @staticmethod
    @serviceinterface
    def get_version(resource_manager):
        """
        Get details for a 'get_version' response by calling relevant methods in the corresponding resource manager.

        If the method is not available, it implies that this field is not required/supported.

        Args:
            resource_manager: Resource Manager instance to request information from

        Returns:
            complete 'get_version' response

        """

        version = {}
        for field in DelegateTools.GET_VERSION_FIELDS:
            if hasattr(resource_manager, field.lower()):
                version[field] = getattr(resource_manager, field.lower())()
        return version


    #<UT>
    @serviceinterface
    def get_default_privilege_list(self, role_, context_):
        """
        Provides a list of privileges for required member role

        Args:
            role_: the member role as mentioned in roles.json files
            context_: Context of member role, e.g., project or slice etc.

        Returns:
            List of privileges for member roles passed as argument
        """
        return self.STATIC['ROLES'][role_][context_]

    #<UT>
    @serviceinterface
    def get_required_privilege_for(self, method_, type_, role_=None):
        """
        Provides a list of privileges required to access a method
        (see authz.json for further details)

        Args:
            method_: Name of the method e.g., CREATE, UPDATE, LOOKUP, DELETE, CHANGE_ROLE etc.
            type_: Type of Object e.g., SLICE, SLICE_MEMBER, PROJECT, PROJECT_MEMBER etc.
            role_: Describes the member role which is required to change. It is only used in conjunction with CHANGE_ROLE

        Returns:
            List of privileges required to access given method
        """
        if role_ is None:
            return self.STATIC['AUTHZ'][method_][type_]
        else:
            return self.STATIC['AUTHZ'][method_][type_][role_]

    @serviceinterface
    def check_if_authorized(self, credentials, method, type_, target_urn=None, fields=None):
        """
        Check if credentials have any of the given privileges
        :param credentials: credential string in SFA format
        :param method: Name of the method e.g., CREATE, UPDATE, LOOKUP, DELETE, CHANGE_ROLE etc.
        :param type_: Type of Object e.g., SLICE, SLICE_MEMBER, PROJECT, PROJECT_MEMBER etc.
        """
        if credentials is None or len(credentials) <= 0:
            raise GFedv2ArgumentError("Passed invalid or no credentials")

        required_privileges = self.get_required_privilege_for(method, type_)
        geniutil = pm.getService('geniutil')
        cred_accepted = False
        for cred in credentials:
            try:
                priv_from_cred, target_urn_from_cred = geniutil.get_privileges_and_target_urn([cred])
                owner_cert = geniutil.extract_owner_certificate([cred])
                user_urn_from_cert, _, _ = geniutil.extract_certificate_info(owner_cert)
                _, cred_typ, _ = geniutil.decode_urn(target_urn_from_cred)
                #If given are system member credentials then target_urn cannot be used in verification
                if user_urn_from_cert == target_urn_from_cred:
                    geniutil.verify_credential_ex([cred], user_urn_from_cert, self.TRUSTED_CERT_PATH, crl_path=self.TRUSTED_CRL_PATH)
                #If project credentials are used to execute commands on slice then context of such credentials must be verified
                elif type_ in ['SLICE', 'SLICE_MEMBER'] and cred_typ == 'project':
                    self.verify_project_credentials_context([cred], method, fields, target_urn)
                    geniutil.verify_credential_ex([cred], target_urn_from_cred, self.TRUSTED_CERT_PATH, crl_path=self.TRUSTED_CRL_PATH)
                # Finally, slice credentials are used for slice objects or project credentials are used for project object
                else:
                    geniutil.verify_credential_ex([cred], target_urn, self.TRUSTED_CERT_PATH, crl_path=self.TRUSTED_CRL_PATH)

                # print required_privileges
                # print priv_from_cred
                if not required_privileges or set(priv_from_cred).intersection(required_privileges):
                    cred_accepted = True
                    break
            except Exception as e:
                print e.message
                pass

        if not cred_accepted:
            raise GFedv2AuthorizationError("Your credentials do not provide enough privileges to execute "+ method + " call on " + type_ + " object")


    @serviceinterface
    def verify_project_credentials_context(self, credentials, method, fields=None, target_urn=None):
        """
        Verify project to slice relationship
        :param credentials: credential string in SFA format
        :param method: Name of the method e.g., CREATE, UPDATE, LOOKUP, DELETE, CHANGE_ROLE etc.
        """

        geniutil = pm.getService('geniutil')
        slice_authority_resource_manager = pm.getService('osliceauthorityrm')
        _, target_urn_from_cred = geniutil.get_privileges_and_target_urn(credentials)
        verification_passed = True

        if method == 'CREATE':
            if not fields['SLICE_PROJECT_URN'] == target_urn_from_cred:
                verification_passed = False
        elif method == 'UPDATE':
            lookup_result = slice_authority_resource_manager.lookup_slice(credentials,
                                                                        {'SLICE_URN': str(target_urn)}, [], {})
            if not lookup_result or not lookup_result[0]['SLICE_PROJECT_URN'] == target_urn_from_cred:
                    verification_passed = False
        elif method == 'LOOKUP':
            pass
        elif method == 'DELETE':
            pass

        if not verification_passed:
            raise GFedv2AuthorizationError("Your project credentials do not provide enough privileges to execute "+ method + " call on slice object")

    @serviceinterface
    def check_if_modify_membership_authorized(self, credentials, options, type_):
        """
        Check if credentials have any of the given privileges; NOTE: target_urn is assumed to be already checked
        Moreover, authorization for remove member is not performed here
        :param credentials: credential string in SFA format
        :param method: Name of the method e.g., CREATE, UPDATE, LOOKUP, DELETE, CHANGE_ROLE etc.
        :param type_: Type of Object e.g., SLICE, SLICE_MEMBER, PROJECT, PROJECT_MEMBER etc.
        """

        geniutil = pm.getService('geniutil')

        priv_from_cred, _ = geniutil.get_privileges_and_target_urn(credentials)
        required_privileges = []

        for option_key, option_value in options.iteritems():
            for member_dict in option_value:
                #Authorization check for ADMIN and LEAD roles
                if type_ == 'PROJECT':
                    if 'PROJECT_ROLE' in member_dict:
                        if member_dict['PROJECT_ROLE'] == 'ADMIN':
                            required_privileges = self.get_required_privilege_for('CHANGE_ROLE', 'PROJECT_MEMBER', 'ADMIN')
                        elif member_dict['PROJECT_ROLE'] == 'LEAD':
                            required_privileges = self.get_required_privilege_for('CHANGE_ROLE', 'PROJECT_MEMBER', 'LEAD')
                        elif member_dict['PROJECT_ROLE'] == 'MONITOR':
                            required_privileges = self.get_required_privilege_for('CHANGE_ROLE', 'PROJECT_MEMBER', 'MONITOR')
                elif type_ == 'SLICE':
                    if 'SLICE_ROLE' in member_dict:
                        if member_dict['SLICE_ROLE'] == 'ADMIN':
                            required_privileges = self.get_required_privilege_for('CHANGE_ROLE', 'SLICE_MEMBER', 'ADMIN')
                        elif member_dict['SLICE_ROLE'] == 'LEAD':
                            required_privileges = self.get_required_privilege_for('CHANGE_ROLE', 'SLICE_MEMBER', 'LEAD')

                if required_privileges and not set(priv_from_cred).intersection(required_privileges):
                    raise GFedv2AuthorizationError("Your credentials do not provide enough privileges to modify "+ type_ +
                                                   " membership\nYour Privileges: "+str(priv_from_cred)+" Required one of following privileges "+str(required_privileges))

                # Only self owned privileges can be assigned to others
                if 'EXTRA_PRIVILEGES' in member_dict:
                    if not set(priv_from_cred).issuperset(member_dict['EXTRA_PRIVILEGES']):
                        raise GFedv2AuthorizationError("Your credentials do not provide enough privileges to modify "+ type_ + " membership")

    @serviceinterface
    def check_if_ma_info_update_authorized(self, credentials, type_, target_urn):
        """
        Performs authorization check on member/key info update
        :param credentials:
        :param options:
        :param type_:
        :return:
        """
        if credentials is None or len(credentials) <= 0 or not isinstance(credentials[0], dict):
            raise GFedv2ArgumentError("Passed invalid or no credentials")

        geniutil = pm.getService('geniutil')
        owner_cert = geniutil.extract_owner_certificate(credentials)
        user_urn_from_cert, _, _ = geniutil.extract_certificate_info(owner_cert)

        #Update is allowed for owner himself. Otherwise, proper credentials should be presented
        if user_urn_from_cert == target_urn:
            geniutil.verify_credential_ex(credentials, target_urn, self.TRUSTED_CERT_PATH, crl_path=self.TRUSTED_CRL_PATH)
        else:
            self.check_if_authorized(credentials=credentials, method='UPDATE', type_=type_, target_urn=None)


    def verify_credentials(self, credentials, target_urn=None):
        """
        Verifies if credentials are valid and trusted. If yes, then returns a list of associated privileges
        :param credentials: credentials to verify
        :param target_urn:  Target object's urn of these credentials
        :return: If verification passed, the a list of privileges associated with the passed credentials
        """

        if credentials is None or len(credentials) <= 0 or not isinstance(credentials[0], dict):
            raise GFedv2ArgumentError("Passed invalid or no credentials")

        geniutil = pm.getService('geniutil')

        priv_from_cred, target_urn_from_cred = geniutil.get_privileges_and_target_urn(credentials)
        owner_cert = geniutil.extract_owner_certificate(credentials)
        user_urn_from_cert, _, _ = geniutil.extract_certificate_info(owner_cert)

        #If given are system member credentials then target_urn cannot be used in verification
        if user_urn_from_cert == target_urn_from_cred:
            geniutil.verify_credential_ex(credentials, user_urn_from_cert, self.TRUSTED_CERT_PATH, crl_path=self.TRUSTED_CRL_PATH)
        else:
            geniutil.verify_credential_ex(credentials, target_urn, self.TRUSTED_CERT_PATH, crl_path=self.TRUSTED_CRL_PATH)

        return priv_from_cred

    def delegate_credentials(self, delegetee_cert, issuer_key, privileges_list, expiration,
                             delegatable, credentials):
        """
        Creates delegated credentials
        """

        if credentials is None or len(credentials) <= 0 or not isinstance(credentials[0], dict):
            raise GFedv2ArgumentError("Passed invalid or no credentials")

        geniutil = pm.getService('geniutil')

        priv_from_cred, target_urn_from_cred = geniutil.get_privileges_and_target_urn(credentials)
        certificate = geniutil.extract_owner_certificate(credentials)

        self.verify_credentials(credentials, target_urn_from_cred)

        if not set(priv_from_cred).issuperset(privileges_list):
            raise GFedv2AuthorizationError("You cannot delegate privileges that you don't own")

        object_cert = geniutil.extract_object_certificate(credentials)

        return geniutil.create_credential_ex(delegetee_cert, object_cert, issuer_key, certificate, privileges_list,
                                             expiration, delegatable, credentials)


    def verify_certificate(self, certificate):
        """
        Verifies if credentials are valid and trusted. If yes, then returns a list of associated privileges
        :param certificate: certificate to verify
        """

        if certificate is None or len(certificate) <= 0:
            raise GFedv2ArgumentError("Passed invalid or no credentials")

        geniutil = pm.getService('geniutil')

        geniutil.verify_certificate(certificate, self.TRUSTED_CERT_PATH, crl_path=self.TRUSTED_CRL_PATH)


    @serviceinterface
    def get_whitelist(self, type_):
        """
        Forms a number of whitelists for a given object type.

        Lists formed include:
            * create_whitelist: fields that can be passed in 'create' operation
            * create_required: fields that must be passed in a 'create' operation
            * update_whitelist: fields that can be passed in an 'update' operation
            * lookup_match: fields that can be passed in a 'lookup' operation's 'match' field
            * lookup_protected: fields that must be protected in a 'lookup' operation
            * lookup_identifying: fields that identify a user in a 'lookup' operation

        Protected and identify information is to be given out according to
        implementation-specific privileges of requesting user

        Args:
            type_: the type of object

        Returns:
            dictionary of whitelists
        """
        combined_fields = self.STATIC['COMBINED'][type_]
        whitelist = {'create_whitelist' : [], 'create_required' : [],
            'update_whitelist' : [], 'lookup_match' : [], 'lookup_private' : [],
            'lookup_identifying' : []}
        for field_key, field_value in combined_fields.iteritems():
            whitelist = self._get_fields_values(whitelist, field_key, field_value)
        return whitelist

    def _get_fields_values(self, whitelist, field_key, field_value):
        """
        Set whitelist values for a given field.

        Fields and defaults as per: http://groups.geni.net/geni/wiki/CommonFederationAPIv2#APIget_versionmethods

        Args:
            whitelist: dictionary of whitelists to update
            field_key: key for field
            field_value: value for field

        Returns:
            dictionary of whitelists

        """
        if field_value.get('CREATE', 'NOT ALLOWED') in ['REQUIRED', 'ALLOWED']:
            whitelist['create_whitelist'].append(field_key)
            if field_value.get('CREATE', False) is 'REQUIRED':
                whitelist['create_required'].append(field_key)
        if field_value.get('MATCH', True):
            whitelist['lookup_match'].append(field_key)
        if field_value.get('UPDATE', False):
            whitelist['update_whitelist'].append(field_key)
        protect = field_value.get('PROTECT', 'PUBLIC')
        if protect is 'IDENTIFYING':
            whitelist['lookup_identifying'].append(field_key)
        if protect is 'PRIVATE':
            whitelist['lookup_private'].append(field_key)
        return whitelist

    @staticmethod
    @serviceinterface
    def member_check(required_field_keys, options):
        """
        Check correctly formed options for 'modify_membership' method.

        Ensures method is one of 'members_to_add', 'members_to_change' or 'members_to_remove'.

        Args:
            required_field_keys: keys to add, change or remove are dependent on object type (Slice Member or Project Member)
            options: call parameters to check

        Raises:
            GFedv2ArgumentError: There is an inconsitency in the options given

        """
        for method_key, method_value in options.iteritems():
            if method_key in DelegateTools.REQUIRED_METHOD_KEYS:
                for item in  method_value:
                    if type(item) is dict: #For compatability with OMNI which send list type for remove_member
                        for field_key in item.iterkeys():
                            if not field_key in required_field_keys:
                                raise GFedv2ArgumentError("Member key to modify not of required type. Offending key is: " +
                                                          str(field_key) + ". Should be one of these types: " +
                                                          str(required_field_keys))
            else:
                raise GFedv2ArgumentError("Member method key not found. Offending key is: " + str(method_key) +
                                                         ". Should be one of these types: " +
                                                            str(DelegateTools.REQUIRED_METHOD_KEYS))

    @staticmethod
    @serviceinterface
    def slice_name_check(slice_name):
        if not re.match(r'^[a-zA-Z0-9][A-Za-z0-9-]{1,19}$', slice_name):
            raise GFedv2ArgumentError('SLICE_NAME field must be <= 19 characters, must only contain alphanumeric '
                                      'characters or hyphens and those hyphens must not be leading.')

    @staticmethod
    @serviceinterface
    def object_creation_check(fields, whitelist):
        """
        Check if the given fields can be used in creating an object.

        Args:
            fields: fields to verify
            whitelist: field names to check against

        Raises:
            GFedv2ArgumentError: There is a required field missing or it is not possible to pass this field during object creation.

        """
        required = set(whitelist.get('create_required')).difference(set(fields))
        whitelist = set(fields).difference(set(whitelist.get('create_whitelist')))
        if required:
            raise GFedv2ArgumentError('Required key(s) missing for object creation: ' + ', '.join(required))
        if whitelist:
            raise GFedv2ArgumentError('Cannot pass the following key(s) when creating an object : ' +
                                      ', '.join(whitelist))

    @staticmethod
    @serviceinterface
    def object_update_check(fields, whitelist):
        """
        Check if the given fields can be used in updating an object.

        Args:
            fields: field names to verify
            whitelist: field names to check against

        Raises:
            GFedv2ArgumentError: It is not possible to pass this field during an object update.

        """

        whitelist = set(fields).difference(set(whitelist.get('update_whitelist')))
        if whitelist:
            raise GFedv2ArgumentError('Cannot pass the following key(s) when updating an object : ' + ', '.join(whitelist))

    @serviceinterface
    def object_consistency_check(self, type_, fields):
        """
        Check that fields conform to a predefined type by calling a corresponding method.

        Args:
            type_: the type of object
            fields: fields to verify

        Raises:
            GFedv2ArgumentError: Inconsistency found between a field value and the required type.

        """

        combined = self.STATIC['COMBINED'][type_]
        for key, value in fields.iteritems():
            if DelegateTools.JSON_COMMENT not in key and value is not None:
                field_type = combined[key.upper()].get('TYPE')

                try:
                    getattr(TypeCheck, 'check_' + field_type.lower())(value)
                except AttributeError:
                    raise GFedv2ArgumentError('No type check available for: ' + field_type + '. Please check your supplementary fields for valid data types. ' +
                        'See http://groups.geni.net/geni/wiki/CommonFederationAPIv2#AppendixB:APIDataTypes for more details.')
                except Exception:
                    raise GFedv2ArgumentError('Field {' + key + ' : ' + str(value) + '} is not of type ' + field_type)
 
    @staticmethod
    @serviceinterface
    def decompose_slice_urns(match_value_to_decompose):
        """
        Create individual SLICE_URN entries to match from a list of SLICE_URN Values. For example,
        input = {SLICE_URN: [urn1, unr2, urn3}
        output =[{SLICE_URN: urn1}, {SLICE_URN:urn2}, {SLICE_URN:urn3}]

        Args:
            match_value_to_decompose: dictionary of individual slice URN list with other match values

        Returns:
            match_urn_list: A list of dictionaries for each slice URN

        """
        match_urn_list=[]
        if 'SLICE_URN' in match_value_to_decompose:
            get_result=match_value_to_decompose.get('SLICE_URN')

            if isinstance(get_result,list):
                urns_to_query=match_value_to_decompose.pop('SLICE_URN')

                for value in urns_to_query:
                    match_value_to_decompose_copy=match_value_to_decompose.copy()
                    match_value_to_decompose_copy['SLICE_URN']=value
                    match_urn_list.append(match_value_to_decompose_copy)
            else:
                match_urn_list.append(match_value_to_decompose)
        else:
            match_urn_list.append(match_value_to_decompose)

        return match_urn_list

    @staticmethod
    @serviceinterface
    def to_keyed_dict(list_, key):
        """
        Convert a list to a dictionary, keyed to given key.

        Args:
            list_: list object use for conversion
            key: field to use as dictionary key

        Returns:
            keyed dictionary

        """
        for d in list_:
            if not key in d:
                raise ValueError("Can not convert to dict because the key_field name (%s) is not in the dictionary (%s)" % (key, d))
        return { d[key] : dict(filter(lambda (k,v): (k != key), d.iteritems())) for d in list_}

    @serviceinterface
    def match_and_filter(self, list_of_dicts, field_filter, field_match):
        """
        Takes a list of dicts and applies the given filter and matches the results (please GENI Federation API on how matching and filtering works).
        if field_filter is None the unfiltered list is returned.
        """
        return [self._filter_fields(d, field_filter) for d in list_of_dicts if self._does_match_fields(d, field_match)]

    def _does_match_fields(self, d, field_match):
        """
        Returns if the given dictionary matches the {field_match}.
        {field_match} may look like: { 'must_be' : 'this', 'and_any_of_' : ['tho', 'se']}
        """
        if not field_match:
            return True
        for mk, mv in field_match.iteritems(): # each matches must be fulfilled
            val = d[mk]
            if isinstance(mv, list): # any of those values (OR)
                found_any = False;
                for mvv in mv:
                    if val == mvv:
                        found_any = True
                if not found_any:
                    return False
            else: # or explicitly this one
                if not val == mv:
                    return False
        return True

    def _filter_fields(self, d, field_filter):
        """Takes a dictionary and applies the filter. Returns the unfiltered d if None is given."""
        if not field_filter:
            return d
        result = {}
        for f in field_filter:
            result[f] = d[f]
        return result

class TypeCheck():
    """
    Used as a holder for various type checks used in 'object_consistency_check' method.
    """

    @staticmethod
    def check_urn(value):
        """
        Check if value is a valid URN string

        See wiki for more details: http://groups.geni.net/geni/wiki/GeniApiIdentifiers

        Args:
            value: item to check

        Raises:
            Exception: value is not of valid URN string

        """
        if not re.match(r"^urn:publicid:IDN+\+[A-Za-z0-9\._:-]+\+[A-Za-z0-9]+\+[A-Za-z0-9\._+:-]*$", value):
            raise Exception

    @staticmethod
    def check_url(value):
        """
        Check if value is a valid URL string

        Args:
            value: item to check

        Raises:
            Exception: value is not of valid URL string

        """
        regex = re.compile(
            r'^(?:http)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not re.match(regex, value):
            raise Exception

    @staticmethod
    def check_uid(value):
        """
        Check if value is a valid UUID string.

        Args:
            value: item to check

        Raises:
            Exception: value is not of valid UID string

        """
        uuid.UUID(value)

    @staticmethod
    def check_string(value):
        """
        Check if value is a valid String.

        Args:
            value: item to check

        Raises:
            Exception: value is not of type String

        """
        if not isinstance(value, basestring):
            raise Exception

    @staticmethod
    def check_integer(value):
        """
        Check if value is a valid Integer.

        Args:
            value: item to check

        Raises:
            Exception: value is not of type Integer

        """
        if not isinstance(value, int):
             raise Exception

    @staticmethod
    def check_datetime(value):
        """
        Check if value is a valid RFC3339 string.

        See RFC3339 for more details: http://www.ietf.org/rfc/rfc3339.txt

        Args:
            value: item to check

        Raises:
            Exception: value is not of valid RFC3339 string

        """
        pyrfc3339.parse(value)

    @staticmethod
    def check_email(value):
        """
        Check if value is a valid email string.

        Args:
            value: item to check

        Raises:
            Exception: value is not of valid email string

        """
        if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", value):
            raise Exception

    @staticmethod
    def check_key(value):
        """
        Check if value is a valid key string.

        Should be contents, rather than filename.
        Incomplete implementation. Only very basic object check currently.

        Args:
            value: item to check

        Raises:
            Exception: value is not of valid key string

        """
        # TODO: check key validity - SSH or SSL public or private key
        if not isinstance(value, basestring):
            raise Exception

    @staticmethod
    def check_boolean(value):
        """
        Check if value is a valid Boolean.

        Args:
            value: item to check

        Raises:
            Exception: value is not of type Boolean

        """
        if not isinstance(value, bool):
            raise Exception

    @staticmethod
    def check_credentials(value):
        """
        Check if value is a valid credential string.

        Should be contents, rather than filename.
        Incomplete implementation. Only very basic object check currently.

        Args:
            value: item to check

        Raises:
            Exception: value is not of valid credential string

        """
        # TODO: check credential validity with geni_trust
        if not isinstance(value, basestring):
            raise Exception

    @staticmethod
    def check_certificate(value):
        """
        Check if value is a valid certificate string.

        Should be contents, rather than filename.
        Incomplete implementation. Only very basic object check currently.

        Args:
            value: item to check

        Raises:
            Exception: value is not of valid certificate string

        """
        # TODO: check certificate validity with geni_trust
        if not isinstance(value, basestring):
            raise Exception

    @staticmethod
    def check_list_of_dictionaries(value):
        """
        Check if value is a valid list of dictionaries.

        Args:
            value: item to check

        Raises:
            Exception: value is not of valid  list of dictionaries

        """
        if not isinstance(value, list):
            raise Exception
        for dictionary in value:
            if not isinstance(dictionary, dict):
                raise Exception