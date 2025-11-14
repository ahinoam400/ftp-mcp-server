import pytest
import subprocess
import time
import os
import sys

@pytest.fixture(scope="session", autouse=True)
def ftp_server():
    # Start the FTP server in a separate process
    server_path = os.path.join(os.path.dirname(__file__), "ftp_server.py")
    process = subprocess.Popen([sys.executable, server_path])
    
    # Give the server some time to start up
    time.sleep(2)
    
    yield
    
    # Terminate the FTP server process after tests are done
    process.terminate()
    process.wait()

