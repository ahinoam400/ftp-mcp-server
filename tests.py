import unittest
import threading
import time
from pathlib import Path
import os
from ftplib import error_perm

from ftp_server import main as ftp_server_main
from ftp_client_logic import (
    ftp_connect,
    ftp_disconnect,
    ftp_list,
    ftp_nlst,
    ftp_mlsd,
    ftp_retrieve_file,
    ftp_store_file,
    ftp_cwd,
    ftp_rename,
    ftp_copy_recursive,
    ftp_delete_recursive,
    ftp_sessions,
)

# FTP Server Configuration
FTP_HOST = "127.0.0.1"
FTP_PORT = 2121
FTP_USER = "user"
FTP_PASS = "12345"
FTP_HOME = Path("ftp_home")


class TestFTPServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure the FTP home directory exists and is clean
        FTP_HOME.mkdir(exist_ok=True)
        for item in FTP_HOME.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                import shutil
                shutil.rmtree(item)


        # Run FTP server in a separate thread
        cls.ftp_server_thread = threading.Thread(target=ftp_server_main, daemon=True)
        cls.ftp_server_thread.start()
        time.sleep(1)  # Give the server a moment to start

        # Create a dummy file for testing uploads
        cls.local_test_file = Path("test_upload.txt")
        cls.local_test_file.write_text("This is a test file for uploads.")

    @classmethod
    def tearDownClass(cls):
        # Clean up the dummy file
        if cls.local_test_file.exists():
            cls.local_test_file.unlink()
        
        # Stop the server by closing all sessions, which might not be enough to stop the thread
        # but it's the best we can do without modifying the server's shutdown logic.
        for session_id in list(ftp_sessions.keys()):
            ftp_disconnect(session_id)


    def setUp(self):
        # Connect to the FTP server for each test
        response = ftp_connect(FTP_HOST, FTP_USER, FTP_PASS, FTP_PORT)
        self.assertTrue("Successfully connected" in response)
        self.session_id = response.split(": ")[-1]

    def tearDown(self):
        # Disconnect from the FTP server after each test
        ftp_disconnect(self.session_id)

    def test_01_list_files(self):
        # Test listing files with LIST, NLST, and MLSD
        for list_func in [ftp_list, ftp_nlst, ftp_mlsd]:
            with self.subTest(list_func=list_func.__name__):
                files = list_func(self.session_id)
                self.assertIsInstance(files, list)

    def test_02_upload_and_download(self):
        # Upload a file
        remote_filename = "uploaded_test_file.txt"
        ftp_store_file(self.session_id, str(self.local_test_file), remote_filename)

        # Verify the file was uploaded
        files = ftp_nlst(self.session_id)
        self.assertIn(remote_filename, files)

        # Download the file and verify its content
        content = ftp_retrieve_file(self.session_id, remote_filename)
        self.assertEqual(content, self.local_test_file.read_text())

        # Clean up the uploaded file
        ftp_delete_recursive(self.session_id, remote_filename)

    def test_03_change_directory(self):
        # Create a test directory on the server
        test_dir = "test_dir_cd"
        ftp = ftp_sessions[self.session_id]
        ftp.mkd(test_dir)

        # Change to the new directory
        response = ftp_cwd(self.session_id, test_dir)
        self.assertTrue("Successfully changed directory" in response)
        self.assertTrue(test_dir in ftp.pwd())

        # Change back to the home directory
        response = ftp_cwd(self.session_id, "/")
        self.assertTrue("Successfully changed directory" in response)
        self.assertFalse(test_dir in ftp.pwd())

        # Clean up the test directory
        ftp_delete_recursive(self.session_id, test_dir)

    def test_04_move_file(self):
        # Upload a file to move
        source = "move_source.txt"
        dest = "move_dest.txt"
        ftp_store_file(self.session_id, str(self.local_test_file), source)

        # Move the file
        ftp_rename(self.session_id, source, dest)

        # Verify the move
        files = ftp_nlst(self.session_id)
        self.assertNotIn(source, files)
        self.assertIn(dest, files)

        # Clean up
        ftp_delete_recursive(self.session_id, dest)

    def test_05_copy_and_delete_recursive(self):
        # Create a nested source directory structure on the server
        source_dir = "source_copy_recursive"
        sub_dir = "subdir"
        ftp = ftp_sessions[self.session_id]
        
        # Create directories
        ftp.mkd(source_dir)
        ftp.mkd(f"{source_dir}/{sub_dir}")

        # Upload files to both directories
        ftp_store_file(self.session_id, str(self.local_test_file), f"{source_dir}/root_file.txt")
        ftp_store_file(self.session_id, str(self.local_test_file), f"{source_dir}/{sub_dir}/sub_file.txt")

        # --- Test Recursive Copy ---
        dest_dir = "dest_copy_recursive"
        ftp_copy_recursive(self.session_id, source_dir, dest_dir)

        # Verify the copy
        root_files = ftp_nlst(self.session_id, dest_dir)
        sub_files = ftp_nlst(self.session_id, f"{dest_dir}/{sub_dir}")

        self.assertIn("root_file.txt", [os.path.basename(f) for f in root_files])
        self.assertIn(sub_dir, [os.path.basename(f) for f in root_files])
        self.assertIn("sub_file.txt", [os.path.basename(f) for f in sub_files])

        # --- Test Recursive Delete ---
        # Clean up the source and destination directories
        ftp_delete_recursive(self.session_id, source_dir)
        ftp_delete_recursive(self.session_id, dest_dir)

        # Verify deletion
        files = ftp_nlst(self.session_id)
        self.assertNotIn(source_dir, files)
        self.assertNotIn(dest_dir, files)


if __name__ == "__main__":
    unittest.main()