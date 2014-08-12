__author__ = 'umar.toseef'
from communication_tools import *


def ma_call(method_name, params=[], user_name='alice'):

    return api_call(method_name, 'ma/2', params=params, user_name=user_name)

def sa_call(method_name, params=[], user_name='expedient'):
    return api_call(method_name, 'sa/2', params=params, user_name=user_name)

def create_slice(slice_name, slice_desc, slice_project_urn='urn:publicid:IDN+this_sa+alien+expedient', user_credentials=''):

    create_data = {'SLICE_NAME': slice_name, 'SLICE_DESCRIPTION': slice_desc, 'SLICE_PROJECT_URN': slice_project_urn}
    code, value, output = sa_call('create', ['SLICE', user_credentials, {'fields': create_data}])

    print 'code:'+str(code)
    print output
    print 'value:'+str(value)

    return (code, value, output)

class test(object):

    """
    An Example to show how a user lookup would work with Ohouse
    """

    def lookup(self, match, object_type, _filter =[] ):
        """
        A sample lookup function which uses dumb ssl certificates and credentials
        Args:
            match: objects to match on e.g., member / user urn
        Return:
            return the result of the event generated
        """
        options = {}
        if match:
            options['match'] = match
        if _filter:
            options['filter'] = _filter
        code, value, output = ma_call('lookup', [object_type, self._credential_list("admin"), options], user_name="admin")

        return value


    """
    def create_slice(self, object_type ='SLICE'):

        create_data = {'SLICE_NAME':'UMARSLICE2', 'SLICE_DESCRIPTION' : 'Umar Clean Slice', 'SLICE_PROJECT_URN' : 'urn:publicid:IDN+this_sa+project+myproject'}

        code, value, output = sa_call('create', ['SLICE', self._credential_list("admin"), {'fields' : create_data}], user_name="admin")
        #code, value, output = sa_call('create', [object_type, self._credential_list("admin"), {'fields' : fields}], user_name="admin")

        return value
    """

    def _credential_list(self, user_name):
        """Returns the _user_ credential for the given user_name."""
        return [{"SFA" : get_creds_file_contents('%s-cred.xml' % (user_name,))}]

