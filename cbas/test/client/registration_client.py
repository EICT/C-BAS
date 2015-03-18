import jsonrpclib

def main():
    """
    Run the Application
    """
    server = jsonrpclib.Server('http://localhost:1234')
    result =  server.register_user('adel', 'zalok', 'alice', 'alice@example.com', 'asdsad')
    print result

if __name__=="__main__":
    main()
