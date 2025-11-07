from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

from pathlib import Path
from ipaddress import IPv4Address

# General Definitions
SERVER_IP = IPv4Address("0.0.0.0")
SERVER_PORT = 2121
FTP_HOME_DIR = Path("ftp_home")
USERNAME1 = "user"
PASSWORD1 = "12345"
FULL_PERMS = "elradfmw"
ANONYMOUS_PERMS = "elr"


def main():
    # Instantiate a dummy authorizer for managing 'virtual' users
    authorizer = DummyAuthorizer()

    # Ensure the FTP home directory exists
    FTP_HOME_DIR.mkdir(exist_ok=True)

    # Define a new user having full permissions on the CWD & anonymous user
    authorizer.add_user("user", "12345", str(FTP_HOME_DIR), perm=FULL_PERMS)
    authorizer.add_anonymous(str(FTP_HOME_DIR), perm=ANONYMOUS_PERMS)

    # Instantiate FTP handler class
    handler = FTPHandler
    handler.authorizer = authorizer

    # --- Passive mode configuration ---
    # Specify a masquerade address if behind a NAT/gateway
    # Replace 'YOUR_PUBLIC_IP' with your actual public IP address
    handler.masquerade_address = '0.0.0.0'
    # Specify the range of ports to use for passive connections
    # These ports must be open in your firewall
    handler.passive_ports = range(60000, 65535) # Example range

    # Define a new server address and port
    address = (str(SERVER_IP), SERVER_PORT)

    # Instantiate FTP server class and listen on the given address
    server = FTPServer(address, handler)

    # Start ftp server. This will run forever, listening for multiple connections.
    server.serve_forever()

if __name__ == "__main__":
    main()
