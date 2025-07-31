from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

def main():
    # Instantiate a dummy authorizer for managing 'virtual' users
    authorizer = DummyAuthorizer()

    # Define a new user having full permissions on the CWD
    import os
    home_dir = os.path.abspath("ftp_home")
    authorizer.add_user("user", "12345", home_dir, perm="elradfmw")

    # Instantiate FTP handler class
    handler = FTPHandler
    handler.authorizer = authorizer

    # Define a new server address and port
    address = ("0.0.0.0", 2121)

    # Instantiate FTP server class and listen on the given address
    server = FTPServer(address, handler)

    # start ftp server
    server.serve_forever()

if __name__ == "__main__":
    main()
