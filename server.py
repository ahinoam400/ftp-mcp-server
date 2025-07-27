from mcp.server.fastmcp import FastMCP
import ftplib
import os

# Initialize the MCP server
mcp = FastMCP("MyPythonServer")

# Global FTP connection object
ftp = None

@mcp.tool()
def ftp_connect(server: str, port: int, user: str, password: str) -> str:
    """
    Connects to an FTP server.

    :param server: The FTP server address.
    :param port: The FTP server port.
    :param user: The username for authentication.
    :param password: The password for authentication.
    :return: A confirmation message.
    """
    global ftp
    try:
        ftp = ftplib.FTP()
        ftp.connect(server, port)
        ftp.login(user, password)
        return "Successfully connected to FTP server."
    except Exception as e:
        return f"Failed to connect to FTP server: {e}"

@mcp.tool()
def ftp_disconnect() -> str:
    """
    Disconnects from the FTP server.

    :return: A confirmation message.
    """
    global ftp
    if ftp:
        ftp.quit()
        ftp = None
        return "Successfully disconnected from FTP server."
    else:
        return "Not connected to any FTP server."

@mcp.tool()
def ftp_list(path: str = ".") -> list:
    """
    Lists files and directories on the FTP server.

    :param path: The path to list. Defaults to the current directory.
    :return: A list of files and directories.
    """
    global ftp
    if ftp:
        try:
            return ftp.nlst(path)
        except Exception as e:
            return [f"Failed to list files: {e}"]
    else:
        return ["Not connected to any FTP server."]

@mcp.tool()
def ftp_get(remote_path: str, local_path: str) -> str:
    """
    Downloads a file from the FTP server.

    :param remote_path: The path of the file to download from the server.
    :param local_path: The local path to save the file to.
    :return: A confirmation message.
    """
    global ftp
    if ftp:
        try:
            with open(local_path, 'wb') as f:
                ftp.retrbinary(f"RETR {remote_path}", f.write)
            return f"Successfully downloaded {remote_path} to {local_path}"
        except Exception as e:
            return f"Failed to download file: {e}"
    else:
        return "Not connected to any FTP server."

@mcp.tool()
def ftp_put(local_path: str, remote_path: str) -> str:
    """
    Uploads a file to the FTP server.

    :param local_path: The path of the local file to upload.
    :param remote_path: The path to save the file to on the server.
    :return: A confirmation message.
    """
    global ftp
    if ftp:
        try:
            with open(local_path, 'rb') as f:
                ftp.storbinary(f"STOR {remote_path}", f)
            return f"Successfully uploaded {local_path} to {remote_path}"
        except Exception as e:
            return f"Failed to upload file: {e}"
    else:
        return "Not connected to any FTP server."

@mcp.tool()
def ftp_cd(path: str) -> str:
    """
    Changes the current directory on the FTP server.

    :param path: The path to change to.
    :return: A confirmation message.
    """
    global ftp
    if ftp:
        try:
            ftp.cwd(path)
            return f"Changed directory to {ftp.pwd()}"
        except Exception as e:
            return f"Failed to change directory: {e}"
    else:
        return "Not connected to any FTP server."

@mcp.tool()
def greet(name: str) -> str:
    """
    A simple tool that returns a greeting.

    :param name: The name of the person to greet.
    :return: A personalized greeting.
    """
    return f"Hello, {name}! This is your custom Python tool."

if __name__ == "__main__":
    mcp.run()
