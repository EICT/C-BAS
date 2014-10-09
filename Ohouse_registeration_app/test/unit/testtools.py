import pexpect
import os
import json
import time


def generate_ssh_keys_pexpect(user_first_name, user_last_name, path):

    """
    Create ssh Keys for the user

    Args:
        user_first_name: The first name of the user which will be included in the URN
        user_last_name: The last name of the user which will be included in the URN
        ch_name: the name of the corresponding clearing house

    """

    try:
        child = pexpect.spawn('ssh-keygen -t rsa')

        child.expect('Enter file in which to save the key (.*):')
        child.sendline(path + '/' + user_first_name + user_last_name)

        child.expect('Enter passphrase (.*):')
        child.sendline('')

        child.expect('Enter same passphrase again:')
        child.sendline('')

    except Exception, e:
        print e #For now


def read_file(path):
    """
    Read a file content

    Args:
        path: The path of the file to read

    Returns:
        The contents of the file
    """
    with file(path) as f:
        s = f.read()
        return s

def write_file(name, contents):
    """
    Write a file content and place in Keys dir

    Args:
        name: The name of the file to create
        contents: Text contents as string

    Returns:
        Nothing
    """
    keys_dir_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../..', 'keys'))
    path = str(keys_dir_path)+ '/' + name

    with open(path,"w") as f:
        f.write(contents)

def read_json_file(path):
    """
    Read content of a JSON file

    Args:
        path: The path of the file to read

    Returns:
        The contents of the JSON file
    """
    with open(path) as json_file:
        json_data = json.load(json_file)
        return json_data


def get_ssh_keys(user_first_name, user_last_name):
    """
    Get ssh keys for a user

    Args:
        user_first_name: The first name of the user which will be included in the URN
        user_last_name: The last name of the user which will be included in the URN

    Returns:
        public ssh key

    """
    keys_dir_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../..', 'keys'))
    public_key_file_path = str(keys_dir_path)+ '/' + user_first_name + user_last_name +'.pub'
    private_key_file_path = str(keys_dir_path)+ '/' + user_first_name + user_last_name

    if os.path.isfile(public_key_file_path):
        os.remove(public_key_file_path)

    if os.path.isfile(private_key_file_path):
        os.remove(private_key_file_path)

    generate_ssh_keys_pexpect(user_first_name, user_last_name, keys_dir_path)

    private_key = read_file(private_key_file_path)
    public_key  = read_file(public_key_file_path)

    return (public_key, private_key)

def get_server_conf(filename):

    conf_dir_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../..', 'configuration'))
    if not os.path.isabs(filename):
        filename = os.path.join(conf_dir_path, filename)
    filename = os.path.abspath(os.path.expanduser(filename))

    conf_data = read_json_file(filename)
    server_ip = conf_data['registration_server']['ip_address']
    server_port = conf_data['registration_server']['port_number']

    return server_ip, server_port

