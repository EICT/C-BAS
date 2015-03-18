import os

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


def write_file(dir_path, file_name, str, silent=False):
    """
    Write content to a file

    Args:
        dir_path: The path of the directory to read
        file_name: The name of the file to write
        str: Content to write to the fil
        silent: A boolean value to print log messages

    """
    path = os.path.join(dir_path, file_name)
    with open(path, 'w') as f:
        f.write(str)
    if not silent:
        print "  Wrote file %s" % (path,)


def delete_keys(dir_path, file_name):
    """
    Read a file content

    Args:
        dir_path: The path of the directory that contains the files
        file_name: The name of the key files

    """
    try:
        path_private_key = os.path.join(dir_path, file_name)
        path_public_key =  os.path.join(dir_path, file_name+'.pub')

        os.remove(path_private_key)
        os.remove(path_public_key)

    except IOError, e:
        print "File does not exist"

