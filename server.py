import asyncio
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from ftp_client_logic import (ftp_connect, ftp_disconnect, ftp_list, ftp_nlst, ftp_mlsd, ftp_retrieve_file,
                              ftp_store_file, ftp_store_file_unique, ftp_cwd, ftp_cwd, ftp_rename, ftp_mkdir,
                              ftp_rmdir, ftp_abort_transfer, ftp_cdup_directory, ftp_set_pasv, ftp_send_port,
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
mcp.tool()(ftp_set_pasv)
mcp.tool()(ftp_send_port)
mcp.tool()(ftp_get_file_size)
mcp.tool()(ftp_send_command)
mcp.tool()(ftp_void_command)
mcp.tool()(ftp_delete_recursive)
mcp.tool()(ftp_copy_recursive)

async def main():
    """
    Runs the MCP server.
    """
    logger.info("Starting MCP server with ftp client functionalities...")
    
    # Start the server asynchronously
    await mcp.run_async()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user.")
    except Exception:
        logger.exception("Unexpected error")