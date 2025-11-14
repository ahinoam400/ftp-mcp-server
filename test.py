# pytest integration test
from fastmcp.exceptions import ToolError
import pytest
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport
import pytest_asyncio



from fastmcp import FastMCP
from ftp_client_logic import (ftp_connect, ftp_disconnect, ftp_list, ftp_nlst, ftp_mlsd, ftp_retrieve_file,
                            ftp_store_file, ftp_store_file_unique, ftp_cwd, ftp_cwd, ftp_rename, ftp_mkdir,
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
