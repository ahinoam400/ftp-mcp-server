# pytest integration test
import pytest
import pytest_asyncio

from fastmcp import FastMCP
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport
from fastmcp.exceptions import ToolError

from ftp_client_logic import (ftp_connect, ftp_disconnect, ftp_list, ftp_nlst, ftp_mlsd, ftp_retrieve_file,
                            ftp_store_file, ftp_store_file_unique, ftp_cwd, ftp_rename, ftp_mkdir,
                            ftp_rmdir, ftp_abort_transfer, ftp_cdup_directory,
                            ftp_get_file_size, ftp_send_command, ftp_void_command, ftp_delete_recursive, 
                            ftp_copy_recursive, logger)

# Initialize the MCP server
mcp = FastMCP("FTPClient")

# Wrap the logic functions with the MCP tool decorator
mcp.tool()(ftp_connect)
mcp.tool()(ftp_disconnect)
mcp.tool()(ftp_list)
mcp.tool()(ftp_nlst)
mcp.tool()(ftp_mlsd)
mcp.tool()(ftp_retrieve_file)
mcp.tool()(ftp_store_file)
mcp.tool()(ftp_store_file_unique)
# Redundant ftp_cwd definition removed
mcp.tool()(ftp_cwd)
mcp.tool()(ftp_rename)
mcp.tool()(ftp_mkdir)
mcp.tool()(ftp_rmdir)
mcp.tool()(ftp_abort_transfer)
mcp.tool()(ftp_cdup_directory)
mcp.tool()(ftp_get_file_size)
mcp.tool()(ftp_send_command)
mcp.tool()(ftp_void_command)
mcp.tool()(ftp_delete_recursive)
mcp.tool()(ftp_copy_recursive)

@pytest_asyncio.fixture
async def main_mcp_client():
    async with Client(transport=mcp) as mcp_client:
        yield mcp_client

@pytest.mark.asyncio
async def test_list_tools(main_mcp_client: Client[FastMCPTransport]):
    list_tools = await main_mcp_client.list_tools()

    assert len(list_tools) == 19


@pytest.mark.asyncio
async def test_ftp_connect_and_disconnect(main_mcp_client: Client[FastMCPTransport]):
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    assert "Successfully connected" in connect_response.data
    
    # Extract session ID from the response
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]
    
    # Disconnect from the FTP server
    disconnect_response = await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})
    assert "disconnected successfully" in disconnect_response.data


@pytest.mark.asyncio
async def test_retrieve_file_content(main_mcp_client: Client[FastMCPTransport]):
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]

    # Retrieve the content of demo.txt
    file_content_response = await main_mcp_client.call_tool("ftp_retrieve_file", {"session_id": session_id, "filename": "demo.txt"})
    assert "Hello world." in file_content_response.data

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})

@pytest.mark.asyncio
async def test_ftp_connect_invalid_credentials(main_mcp_client: Client[FastMCPTransport]):
    # Attempt to connect with invalid credentials
    with pytest.raises(ToolError) as excinfo:
        await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "invalid", "password": "invalid"})
    
    assert "Authentication failed" in str(excinfo.value) or "Login incorrect" in str(excinfo.value)

@pytest.mark.asyncio
async def test_ftp_nlst(main_mcp_client: Client[FastMCPTransport]):
    """Tests the ftp_nlst tool (names only list)."""
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]

    # Call the nlst tool
    nlst_response = await main_mcp_client.call_tool("ftp_nlst", {"session_id": session_id, "directory": "/"})
    
    # Check assertions
    assert isinstance(nlst_response.data, list)
    assert "demo.txt" in nlst_response.data, "demo.txt not found in NLST response"

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})

@pytest.mark.asyncio
async def test_ftp_mlsd(main_mcp_client: Client[FastMCPTransport]):
    """Tests the ftp_mlsd tool (machine-readable list)."""
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]

    # Call the mlsd tool
    mlsd_response = await main_mcp_client.call_tool("ftp_mlsd", {"session_id": session_id, "directory": "/"})
    
    # Check assertions
    assert isinstance(mlsd_response.data, list)
    assert len(mlsd_response.data) > 0
    assert "Root()" in str(mlsd_response.data[0]), "MLSD response does not contain expected Root() object"

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})


@pytest.mark.asyncio
async def test_ftp_store_new_file(main_mcp_client: Client[FastMCPTransport]):
    """Tests the ftp_store_file tool for uploading a new file."""
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]

    local_filepath = "temp_upload.txt"
    remote_filename = "uploaded_new_file.txt"

    # Upload the new file
    store_response = await main_mcp_client.call_tool("ftp_store_file", {"session_id": session_id, "local_filepath": local_filepath, "remote_filename": remote_filename})
    assert f"File '{local_filepath}' uploaded successfully." in store_response.data

    # Verify the file exists on the server by listing the directory
    nlst_response = await main_mcp_client.call_tool("ftp_nlst", {"session_id": session_id, "directory": "/"})
    assert remote_filename in nlst_response.data

    # Clean up: delete the uploaded file from the server
    await main_mcp_client.call_tool("ftp_delete_recursive", {"session_id": session_id, "remote_path": remote_filename})

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})


@pytest.mark.asyncio
async def test_ftp_retrieve_non_existent_file(main_mcp_client: Client[FastMCPTransport]):
    """Tests the ftp_retrieve_file tool for a non-existent file."""
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]

    # Attempt to retrieve a non-existent file
    with pytest.raises(ToolError) as excinfo:
        await main_mcp_client.call_tool("ftp_retrieve_file", {"session_id": session_id, "filename": "non_existent_file.txt"})
    
    assert "Error retrieving file content" in str(excinfo.value) or "No such file or directory" in str(excinfo.value)

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})


@pytest.mark.asyncio
async def test_ftp_retrieve_existing_file(main_mcp_client: Client[FastMCPTransport]):
    """Tests the ftp_retrieve_file tool for an existing file."""
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]

    # Retrieve the content of demo.txt
    file_content_response = await main_mcp_client.call_tool("ftp_retrieve_file", {"session_id": session_id, "filename": "demo.txt"})
    assert "Hello world." in file_content_response.data

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})

@pytest.mark.asyncio
async def test_ftp_store_overwrite_file(main_mcp_client: Client[FastMCPTransport]):
    """Tests the ftp_store_file tool for overwriting an existing file."""
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]

    local_filepath = "temp_overwrite.txt"
    remote_filename = "demo.txt"

    # Get original content of demo.txt to restore later
    original_content_response = await main_mcp_client.call_tool("ftp_retrieve_file", {"session_id": session_id, "filename": remote_filename})
    original_content = original_content_response.data

    # Upload the new file to overwrite demo.txt
    store_response = await main_mcp_client.call_tool("ftp_store_file", {"session_id": session_id, "local_filepath": local_filepath, "remote_filename": remote_filename})
    assert f"File '{local_filepath}' uploaded successfully." in store_response.data

    # Verify the content of demo.txt has changed
    new_content_response = await main_mcp_client.call_tool("ftp_retrieve_file", {"session_id": session_id, "filename": remote_filename})
    assert "OVERWRITE" in new_content_response.data
    assert original_content != new_content_response.data

    # Restore original content of demo.txt
    with open("temp_upload.txt", "w") as f:
        f.write(original_content)
    await main_mcp_client.call_tool("ftp_store_file", {"session_id": session_id, "local_filepath": "temp_upload.txt", "remote_filename": remote_filename})

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})


@pytest.mark.asyncio
async def test_ftp_store_file_unique(main_mcp_client: Client[FastMCPTransport]):
    """Tests the ftp_store_file_unique tool for uploading a file with a unique name."""
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]

    local_filepath = "temp_upload.txt"

    # Upload the file with a unique name
    store_unique_response = await main_mcp_client.call_tool("ftp_store_file_unique", {"session_id": session_id, "local_filepath": local_filepath})
    assert "File uploaded successfully with unique name:" in store_unique_response.data
    
    unique_filename = store_unique_response.data.split(": ")[1]

    # Verify the file exists on the server by listing the directory
    nlst_response = await main_mcp_client.call_tool("ftp_nlst", {"session_id": session_id, "directory": "/"})
    assert unique_filename in nlst_response.data

    # Clean up: delete the uploaded file from the server
    await main_mcp_client.call_tool("ftp_delete_recursive", {"session_id": session_id, "remote_path": unique_filename})

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})


@pytest.mark.asyncio
async def test_ftp_mkdir(main_mcp_client: Client[FastMCPTransport]):
    """Tests the ftp_mkdir tool for creating a new directory."""
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]

    directory_name = "test_mkdir_dir"

    # Cleanup before test: ensure the directory does not exist
    try:
        await main_mcp_client.call_tool("ftp_delete_recursive", {"session_id": session_id, "remote_path": directory_name})
    except ToolError:
        pass  # Directory does not exist, which is fine

    # Create the new directory
    mkdir_response = await main_mcp_client.call_tool("ftp_mkdir", {"session_id": session_id, "directory_name": directory_name})
    assert f"Successfully created directory '{directory_name}'." in mkdir_response.data

    # Verify the directory exists on the server by listing the directory
    nlst_response = await main_mcp_client.call_tool("ftp_nlst", {"session_id": session_id, "directory": "/"})
    assert directory_name in nlst_response.data

    # Clean up: delete the created directory from the server
    await main_mcp_client.call_tool("ftp_rmdir", {"session_id": session_id, "directory_name": directory_name})

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})


@pytest.mark.asyncio
async def test_ftp_cwd(main_mcp_client: Client[FastMCPTransport]):
    """Tests the ftp_cwd tool for changing the current working directory."""
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]

    directory_name = "test_cwd_dir"

    # Change the current working directory
    cwd_response = await main_mcp_client.call_tool("ftp_cwd", {"session_id": session_id, "directory": directory_name})
    assert f"Successfully changed directory to '/{directory_name}'" in cwd_response.data

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})


@pytest.mark.asyncio
async def test_ftp_cdup_directory(main_mcp_client: Client[FastMCPTransport]):
    """Tests the ftp_cdup_directory tool for changing to the parent directory."""
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]

    directory_name = "test_cdup_dir"

    # Create a directory to change into
    await main_mcp_client.call_tool("ftp_mkdir", {"session_id": session_id, "directory_name": directory_name})

    # Change into the directory
    await main_mcp_client.call_tool("ftp_cwd", {"session_id": session_id, "directory": directory_name})

    # Change to the parent directory
    cdup_response = await main_mcp_client.call_tool("ftp_cdup_directory", {"session_id": session_id})
    assert "Successfully moved to parent directory." in cdup_response.data

    # Clean up: delete the created directory from the server
    await main_mcp_client.call_tool("ftp_rmdir", {"session_id": session_id, "directory_name": directory_name})

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})


@pytest.mark.asyncio
async def test_ftp_rmdir_empty(main_mcp_client: Client[FastMCPTransport]):
    """Tests the ftp_rmdir tool for removing an empty directory."""
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]

    directory_name = "test_rmdir_empty_dir"

    # Create the new directory
    await main_mcp_client.call_tool("ftp_mkdir", {"session_id": session_id, "directory_name": directory_name})

    # Remove the empty directory
    rmdir_response = await main_mcp_client.call_tool("ftp_rmdir", {"session_id": session_id, "directory_name": directory_name})
    assert f"Successfully removed directory '{directory_name}'." in rmdir_response.data

    # Verify the directory does not exist on the server by listing the directory
    nlst_response = await main_mcp_client.call_tool("ftp_nlst", {"session_id": session_id, "directory": "/"})
    assert directory_name not in nlst_response.data

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})


@pytest.mark.asyncio
async def test_ftp_rmdir_non_empty(main_mcp_client: Client[FastMCPTransport]):
    """Tests the ftp_rmdir tool for attempting to remove a non-empty directory."""
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]

    directory_name = "test_rmdir_non_empty_dir"

    # Create the new directory
    await main_mcp_client.call_tool("ftp_mkdir", {"session_id": session_id, "directory_name": directory_name})

    # Upload a file to the directory to make it non-empty
    await main_mcp_client.call_tool("ftp_store_file", {"session_id": session_id, "local_filepath": "temp_upload.txt", "remote_filename": f"{directory_name}/uploaded_file.txt"})

    # Attempt to remove the non-empty directory
    with pytest.raises(ToolError) as excinfo:
        await main_mcp_client.call_tool("ftp_rmdir", {"session_id": session_id, "directory_name": directory_name})
    assert "550" in str(excinfo.value)  # FTP error code for directory not empty

    # Clean up: delete the file and the directory
    await main_mcp_client.call_tool("ftp_delete_recursive", {"session_id": session_id, "remote_path": directory_name})

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})


@pytest.mark.asyncio
async def test_ftp_rename_file(main_mcp_client: Client[FastMCPTransport]):
    """Tests the ftp_rename tool for renaming a file."""
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]

    original_filename = "demo.txt"
    new_filename = "renamed_demo.txt"

    # Rename the file
    rename_response = await main_mcp_client.call_tool("ftp_rename", {"session_id": session_id, "from_name": original_filename, "to_name": new_filename})
    assert f"Successfully renamed '{original_filename}' to '{new_filename}'." in rename_response.data

    # Verify the new file exists and the old file does not
    nlst_response = await main_mcp_client.call_tool("ftp_nlst", {"session_id": session_id, "directory": "/"})
    assert new_filename in nlst_response.data
    assert original_filename not in nlst_response.data

    # Clean up: rename the file back to its original name
    await main_mcp_client.call_tool("ftp_rename", {"session_id": session_id, "from_name": new_filename, "to_name": original_filename})

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})


@pytest.mark.asyncio
async def test_ftp_rename_directory(main_mcp_client: Client[FastMCPTransport]):
    """Tests the ftp_rename tool for renaming a directory."""
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]

    original_dirname = "test_rename_dir_original"
    new_dirname = "test_rename_dir_new"

    # Create a directory to rename
    await main_mcp_client.call_tool("ftp_mkdir", {"session_id": session_id, "directory_name": original_dirname})

    # Rename the directory
    rename_response = await main_mcp_client.call_tool("ftp_rename", {"session_id": session_id, "from_name": original_dirname, "to_name": new_dirname})
    assert f"Successfully renamed '{original_dirname}' to '{new_dirname}'." in rename_response.data

    # Verify the new directory exists and the old directory does not
    nlst_response = await main_mcp_client.call_tool("ftp_nlst", {"session_id": session_id, "directory": "/"})
    assert new_dirname in nlst_response.data
    assert original_dirname not in nlst_response.data

    # Clean up: delete the new directory
    await main_mcp_client.call_tool("ftp_rmdir", {"session_id": session_id, "directory_name": new_dirname})

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})


@pytest.mark.asyncio
async def test_ftp_delete_recursive_file(main_mcp_client: Client[FastMCPTransport]):
    """Tests the ftp_delete_recursive tool for deleting a file."""
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]

    filename_to_delete = "temp_file_to_delete.txt"

    # Create a temporary file to delete
    await main_mcp_client.call_tool("ftp_store_file", {"session_id": session_id, "local_filepath": "temp_upload.txt", "remote_filename": filename_to_delete})

    # Verify the file exists
    nlst_response = await main_mcp_client.call_tool("ftp_nlst", {"session_id": session_id, "directory": "/"})
    assert filename_to_delete in nlst_response.data

    # Delete the file
    delete_response = await main_mcp_client.call_tool("ftp_delete_recursive", {"session_id": session_id, "remote_path": filename_to_delete})
    assert f"Successfully deleted '{filename_to_delete}'." in delete_response.data

    # Verify the file does not exist
    nlst_response = await main_mcp_client.call_tool("ftp_nlst", {"session_id": session_id, "directory": "/"})
    assert filename_to_delete not in nlst_response.data

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})


@pytest.mark.asyncio
async def test_ftp_delete_recursive_non_empty_directory(main_mcp_client: Client[FastMCPTransport]):
    """Tests the ftp_delete_recursive tool for deleting a non-empty directory."""
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]

    dirname_to_delete = "test_dir_to_delete"
    nested_file = f"{dirname_to_delete}/nested_file.txt"
    nested_dir = f"{dirname_to_delete}/nested_dir"
    double_nested_file = f"{nested_dir}/double_nested_file.txt"

    # Create a non-empty directory structure
    await main_mcp_client.call_tool("ftp_mkdir", {"session_id": session_id, "directory_name": dirname_to_delete})
    await main_mcp_client.call_tool("ftp_store_file", {"session_id": session_id, "local_filepath": "temp_upload.txt", "remote_filename": nested_file})
    await main_mcp_client.call_tool("ftp_mkdir", {"session_id": session_id, "directory_name": nested_dir})
    await main_mcp_client.call_tool("ftp_store_file", {"session_id": session_id, "local_filepath": "temp_upload.txt", "remote_filename": double_nested_file})

    # Verify the directory and its contents exist
    nlst_response_root = await main_mcp_client.call_tool("ftp_nlst", {"session_id": session_id, "directory": "/"})
    assert dirname_to_delete in nlst_response_root.data
    nlst_response_nested = await main_mcp_client.call_tool("ftp_nlst", {"session_id": session_id, "directory": dirname_to_delete})
    assert "nested_file.txt" in nlst_response_nested.data
    assert "nested_dir" in nlst_response_nested.data
    nlst_response_double_nested = await main_mcp_client.call_tool("ftp_nlst", {"session_id": session_id, "directory": nested_dir})
    assert "double_nested_file.txt" in nlst_response_double_nested.data

    # Delete the non-empty directory recursively
    delete_response = await main_mcp_client.call_tool("ftp_delete_recursive", {"session_id": session_id, "remote_path": dirname_to_delete})
    assert f"Successfully deleted '{dirname_to_delete}'." in delete_response.data

    # Verify the directory and its contents do not exist
    nlst_response_root_after_delete = await main_mcp_client.call_tool("ftp_nlst", {"session_id": session_id, "directory": "/"})
    assert dirname_to_delete not in nlst_response_root_after_delete.data

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})


@pytest.mark.asyncio
async def test_ftp_copy_recursive_file(main_mcp_client: Client[FastMCPTransport]):
    """Tests the ftp_copy_recursive tool for copying a file."""
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]

    source_file = "demo.txt"
    destination_file = "copied_demo.txt"

    # Copy the file
    copy_response = await main_mcp_client.call_tool("ftp_copy_recursive", {"session_id": session_id, "source_path": source_file, "destination_path": destination_file})
    assert f"Successfully copied '{source_file}' to '{destination_file}'." in copy_response.data

    # Verify the copied file exists
    nlst_response = await main_mcp_client.call_tool("ftp_nlst", {"session_id": session_id, "directory": "/"})
    assert destination_file in nlst_response.data

    # Clean up: delete the copied file
    await main_mcp_client.call_tool("ftp_delete_recursive", {"session_id": session_id, "remote_path": destination_file})

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})


@pytest.mark.asyncio
async def test_ftp_copy_recursive_directory(main_mcp_client: Client[FastMCPTransport]):
    """Tests the ftp_copy_recursive tool for copying a directory."""
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]

    source_dir = f"test_copy_source_dir_{session_id}"
    destination_dir = f"test_copy_dest_dir_{session_id}"
    nested_file_in_source = f"{source_dir}/nested_file.txt"

    # Cleanup before test: ensure the directories do not exist
    try:
        await main_mcp_client.call_tool("ftp_delete_recursive", {"session_id": session_id, "remote_path": source_dir})
    except ToolError:
        pass
    try:
        await main_mcp_client.call_tool("ftp_delete_recursive", {"session_id": session_id, "remote_path": destination_dir})
    except ToolError:
        pass

    # Make sure source_dir exists and has a file
    await main_mcp_client.call_tool("ftp_mkdir", {"session_id": session_id, "directory_name": source_dir})
    await main_mcp_client.call_tool("ftp_store_file", {"session_id": session_id, "local_filepath": "temp_upload.txt", "remote_filename": nested_file_in_source})

    # Copy the directory
    copy_response = await main_mcp_client.call_tool("ftp_copy_recursive", {"session_id": session_id, "source_path": source_dir, "destination_path": destination_dir})
    assert f"Successfully copied '{source_dir}' to '{destination_dir}'." in copy_response.data

    # Verify the copied directory and its contents exist
    nlst_response_root = await main_mcp_client.call_tool("ftp_nlst", {"session_id": session_id, "directory": "/"})
    assert destination_dir in nlst_response_root.data
    nlst_response_destination = await main_mcp_client.call_tool("ftp_nlst", {"session_id": session_id, "directory": destination_dir})
    assert "nested_file.txt" in nlst_response_destination.data

    # Clean up: delete source and destination directories
    await main_mcp_client.call_tool("ftp_delete_recursive", {"session_id": session_id, "remote_path": source_dir})
    await main_mcp_client.call_tool("ftp_delete_recursive", {"session_id": session_id, "remote_path": destination_dir})

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})


@pytest.mark.asyncio
async def test_ftp_get_file_size(main_mcp_client: Client[FastMCPTransport]):
    """Tests the ftp_get_file_size tool for getting the size of an existing file."""
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]

    filename = "demo.txt"

    # Get the file size
    size_response = await main_mcp_client.call_tool("ftp_get_file_size", {"session_id": session_id, "file_path": filename})
    assert "File size:" in size_response.data
    assert "bytes." in size_response.data

    # Optionally, verify the size is a positive integer
    size_str = size_response.data.split(": ")[1].split(" ")[0]
    assert int(size_str) > 0

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})


    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})


@pytest.mark.asyncio
async def test_ftp_void_command(main_mcp_client: Client[FastMCPTransport]):
    """Tests the ftp_void_command tool for sending a void command (e.g., NOOP)."""
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]

    command = "NOOP"

    # Send a void command (NOOP should return a success message)
    void_command_response = await main_mcp_client.call_tool("ftp_void_command", {"session_id": session_id, "command": command})
    assert f"Command '{command}' sent successfully." in void_command_response.data

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})


@pytest.mark.asyncio
async def test_ftp_abort_transfer(main_mcp_client: Client[FastMCPTransport]):
    """Tests the ftp_abort_transfer tool."""
    # Connect to the FTP server
    connect_response = await main_mcp_client.call_tool("ftp_connect", {"host": "127.0.0.1", "port": 2121, "username": "user", "password": "12345"})
    session_id = connect_response.data.split("Your session ID is: ")[1].split(".")[0]

    # Call abort transfer (even if no transfer is in progress, it should return success or a handled error)
    abort_response = await main_mcp_client.call_tool("ftp_abort_transfer", {"session_id": session_id})
    assert "Previous command aborted successfully." in abort_response.data

    # Disconnect from the FTP server
    await main_mcp_client.call_tool("ftp_disconnect", {"session_id": session_id})
