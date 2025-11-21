# MCP Tools Test Plan

This file outlines the tasks required to create comprehensive tests for all MCP tools in the project.

## Connection Tools
- [x] Test `ftp_connect`: Successful connection with valid credentials.
- [x] Test `ftp_connect`: Failed connection with invalid credentials.
- [x] Test `ftp_disconnect`: Successful disconnection.

## Directory Listing Tools
- [x] Test `ftp_list`: List contents of the root directory.
- [x] Test `ftp_nlst`: List contents of the root directory (names only).
- [x] Test `ftp_mlsd`: List contents of the root directory (machine-readable).

## File Transfer Tools
- [x] Test `ftp_retrieve_file`: Retrieve an existing file.
- [x] Test `ftp_retrieve_file`: Attempt to retrieve a non-existent file.
- [x] Test `ftp_store_file`: Upload a new file.
- [x] Test `ftp_store_file`: Overwrite an existing file.
- [ ] Test `ftp_store_file_unique`: Upload a file and verify a unique name is generated.

## Directory Management Tools
- [x] Test `ftp_mkdir`: Create a new directory.
- [x] Test `ftp_cwd`: Change the current working directory.
- [x] Test `ftp_cdup_directory`: Change to the parent directory.
- [x] Test `ftp_rmdir`: Remove an empty directory.
- [x] Test `ftp_rmdir`: Attempt to remove a non-empty directory.

## File and Directory Manipulation Tools
- [x] Test `ftp_rename`: Rename a file.
- [x] Test `ftp_rename`: Rename a directory.
- [x] Test `ftp_delete_recursive`: Delete a file.
- [x] Test `ftp_delete_recursive`: Delete a non-empty directory.
- [x] Test `ftp_copy_recursive`: Copy a file.
- [x] Test `ftp_copy_recursive`: Copy a directory.

## Miscellaneous Tools
- [x] Test `ftp_get_file_size`: Get the size of an existing file.
- [x] Test `ftp_send_command`: Send a simple command (e.g., `NOOP`).
- [x] Test `ftp_void_command`: Send a void command (e.g., `NOOP`).
- [x] Test `ftp_abort_transfer`: Abort a file transfer (requires a long-running transfer to test effectively).
