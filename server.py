import asyncio
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from ftp_client_logic import (
    ftp_connect as ftp_connect_logic,
    ftp_disconnect as ftp_disconnect_logic,
    ftp_list as ftp_list_logic,
    ftp_nlst as ftp_nlst_logic,
    ftp_mlsd as ftp_mlsd_logic,
    ftp_get as ftp_get_logic,
    ftp_put as ftp_put_logic,
    ftp_delete_recursive as ftp_delete_recursive_logic,
    ftp_move as ftp_move_logic,
    ftp_copy_recursive as ftp_copy_recursive_logic,
    ftp_cd as ftp_cd_logic,
    logger,
)

# Initialize the MCP server
mcp = FastMCP("FTPClient")

# Wrap the logic functions with the MCP tool decorator
mcp.tool()(ftp_connect_logic)
mcp.tool()(ftp_disconnect_logic)
mcp.tool()(ftp_list_logic)
mcp.tool()(ftp_nlst_logic)
mcp.tool()(ftp_mlsd_logic)
mcp.tool()(ftp_get_logic)
mcp.tool()(ftp_put_logic)
mcp.tool()(ftp_delete_recursive_logic)
mcp.tool()(ftp_move_logic)
mcp.tool()(ftp_copy_recursive_logic)
mcp.tool()(ftp_cd_logic)


async def main():
    """
    Main function that runs the MCP server.
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
        logger.exception("Unexpected error in main loop")