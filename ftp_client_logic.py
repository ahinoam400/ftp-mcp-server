import logging
import uuid
from ftplib import FTP, all_errors, error_perm
from pathlib import Path
from typing import List, Optional, Dict, Any
import io

# Create a custom logger
LOGGER_NAME = "MCP_FTP_Client_Logic"
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.INFO)

# Create a formatter for the log messages
formatter = logging.Formatter("[%(asctime)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

# Create a handler to write logs to a file
LOG_FILE_PATH = Path("mcp_ftp_client.log")
file_handler = logging.FileHandler(LOG_FILE_PATH.absolute())
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Create a handler to print logs to the console
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


# Dictionary of active FTP sessions
ftp_sessions: Dict[str, FTP] = {}

class ToolError(Exception):
    """Custom exception for tool errors."""
    pass

def _check_session(session_id: str) -> FTP:
    """
    Helper function to validate and retrieve an active FTP connection.
    :param session_id: The unique ID of the session.
    :return: The ftplib.FTP object.
    :raises ToolError: If the session ID is invalid or the connection is closed.
    """
    ftp = ftp_sessions.get(session_id)
    if not ftp:
        raise ToolError(f"Session with ID '{session_id}' not found. Please connect first.")
    
    try:
        # A simple command to check if the connection is still alive
        ftp.voidcmd('NOOP')
    except (all_errors, error_perm):
        logger.warning(f"Session '{session_id}' timed out or was closed. Removing from session store.")
        del ftp_sessions[session_id]
        raise ToolError(f"Session with ID '{session_id}' timed out or was disconnected. Please reconnect.")

    return ftp

def ftp_connect(host: str, username: str, password: str, port: int = 21) -> str:
    """
    Connects to an FTP server.

    :param host: The FTP server address.
    :param username: The username for authentication.
    :param password: The password for authentication.
    :param port: The FTP server port.
    :return: A confirmation message containing the unique session ID.
    """
    try:
        session_id = str(uuid.uuid4()) # Generate unique session ID

        ftp = FTP()
        ftp.connect(host, port)
        ftp.login(user=username, passwd=password)

        ftp_sessions[session_id] = ftp
        logger.info(f"New session '{session_id}' established for user '{username}' on host '{host}'.")
        return f"Successfully connected to the FTP server. Your session ID is: {session_id}"
    except Exception as e:
        logger.exception(f"Failed to connect to FTP server '{host}' with user '{username}'.")
        raise ToolError(f"Failed to connect to FTP server: {e}")

def ftp_disconnect(session_id: str) -> str:
    """
    Disconnects from the FTP server.
    
    :param session_id: The unique ID of the active session.
    :return: A success or error message.
    """
    ftp = ftp_sessions.get(session_id)
    if ftp:
        try:
            ftp.quit()
            del ftp_sessions[session_id]
            logger.info(f"Session '{session_id}' has been closed.")
            return f"Session '{session_id}' disconnected successfully."
        except Exception as e:
            logger.exception(f"Error while disconnecting session '{session_id}'.")
            raise ToolError(f"Error while disconnecting session '{session_id}': {e}")
    else:
        return f"Session with ID '{session_id}' was not found or already disconnected."
    
def ftp_nlst(session_id: str, directory: str = ".") -> List[str]:
    """
    Lists the contents of a directory on a remote FTP server using the NLST command.
    Returns a simple list of filenames.
    
    :param session_id: The unique ID of the active session.
    :param directory: The directory to list. Defaults to the user's current directory.
    :return: A list of filenames in the specified directory.
    """
    ftp = _check_session(session_id)
    files = []
    try:
        original_cwd = ftp.pwd()

        ftp.cwd(directory)
        files = ftp.nlst()
        ftp.cwd(original_cwd)

        logger.info(f"NLST: Listed directory '{directory}' for session '{session_id}'.")
        return files
    except Exception as e:
        logger.exception(f"Error listing directory '{directory}' (NLST) for session '{session_id}'.")
        raise ToolError(f"Error listing directory (NLST): {e}")

def ftp_list(session_id: str, directory: str = ".") -> List[str]:
    """
    Lists the contents of a directory on a remote FTP server using the LIST command.
    Returns a raw, unparsed list of strings containing detailed file information.
    
    :param session_id: The unique ID of the active session.
    :param directory: The directory to list. Defaults to the user's current directory.
    :return: A list of raw strings with file details.
    """
    ftp = _check_session(session_id)
    file_lines = []
    try:
        original_cwd = ftp.pwd()

        ftp.cwd(directory)
        ftp.retrlines('LIST', file_lines.append)
        ftp.cwd(original_cwd)

        logger.info(f"LIST: Listed directory '{directory}' for session '{session_id}'.")
        return file_lines
    except Exception as e:
        logger.exception(f"Error listing directory '{directory}' (LIST) for session '{session_id}'.")
        raise ToolError(f"Error listing directory (LIST): {e}")
        
def ftp_mlsd(session_id: str, directory: str = ".") -> List[Dict[str, Any]]:
    """
    Lists the contents of a directory on a remote FTP server using the MLSD command.
    Returns a structured list of dictionaries, with each dictionary containing a filename and its attributes.
    
    :param session_id: The unique ID of the active session.
    :param directory: The directory to list. Defaults to the user's current directory.
    :return: A structured list of dictionaries with file information.
    """
    ftp = _check_session(session_id)
    structured_listing = {}
    try:
        original_cwd = ftp.pwd()

        ftp.cwd(directory)
        if not hasattr(ftp, 'mlsd'):
            raise ToolError("MLSD command not supported by this FTP server or Python version.")
            
        listing = list(ftp.mlsd())
        structured_listing = [{"filename": filename, "attributes": attributes} for filename, attributes in listing]               
        
        ftp.cwd(original_cwd)

        logger.info(f"MLSD: Listed directory '{directory}' for session '{session_id}'.")
        return structured_listing
    except Exception as e:
        logger.exception(f"Error listing directory '{directory}' (MLSD) for session '{session_id}'.")
        raise ToolError(f"Error listing directory (MLSD): {e}")
    
def ftp_get(session_id: str, filename: str) -> str:
    """
    Retrieves a file from a FTP server using an active session.

    :param session_id: The unique ID of the active session.
    :param filename: The name of the file to retrieve.
    :return: The content of the file as a string.
    """
    ftp = _check_session(session_id)
    content_list = []
    try:
        ftp.retrlines(f"RETR {filename}", content_list.append)
        content = "\n".join(content_list)
        logger.info(f"Retrieved content of '{filename}' for session '{session_id}'.")
        return content
    except Exception as e:
        logger.exception(f"Error retrieving file '{filename}' for session '{session_id}'.")
        raise ToolError(f"Error retrieving file content: {e}")

def ftp_put(session_id: str, local_filepath: str, remote_filename: Optional[str] = None) -> str:
    """
    Uploads a local file to a remote FTP server using an active session.
    
    :param session_id: The unique ID of the active session.
    :param local_filepath: The path to the local file to upload.
    :param remote_filename: The name to save the file as on the server. If None, uses the local filename.
    :return: A success message.
    """
    ftp = _check_session(session_id)
    try:
        if not Path(local_filepath).exists():
            raise ToolError(f"Local file not found: {local_filepath}")
            
        remote_filename = remote_filename or Path(local_filepath).name
        with open(local_filepath, 'rb') as f:
            ftp.storbinary(f"STOR {remote_filename}", f)
            
        logger.info(f"Uploaded '{local_filepath}' to '{remote_filename}' for session '{session_id}'.")
        return f"File '{local_filepath}' uploaded successfully."
    except Exception as e:
        logger.exception(f"Error uploading '{local_filepath}' to session '{session_id}'.")
        raise ToolError(f"Error uploading file: {e}")

def ftp_delete_recursive(session_id: str, remote_path: str) -> str:
    """
    Recursively deletes a file or directory on the remote FTP server.

    :param session_id: The unique ID of the active session.
    :param remote_path: The path to the file or directory to delete.
    :return: A success message.
    """
    ftp = _check_session(session_id)
    try:
        # Check if the path is a directory or a file
        try:
            original_cwd = ftp.pwd()
            ftp.cwd(remote_path)
            is_directory = True
            ftp.cwd(original_cwd)
        except error_perm:
            is_directory = False

        if is_directory:
            # It's a directory, so we need to recursively delete its contents
            for name, attrs in ftp.mlsd(path=remote_path):
                if name not in ('.', '..'):
                    ftp_delete_recursive(session_id, f"{remote_path}/{name}")
            ftp.rmd(remote_path)
            logger.info(f"Recursively deleted directory '{remote_path}' for session '{session_id}'.")
        else:
            # It's a file, so we can just delete it
            ftp.delete(remote_path)
            logger.info(f"Deleted file '{remote_path}' for session '{session_id}'.")

        return f"Successfully deleted '{remote_path}'."
    except Exception as e:
        logger.exception(f"Error deleting '{remote_path}' for session '{session_id}'.")
        raise ToolError(f"Error deleting '{remote_path}': {e}")

def ftp_move(session_id: str, source_path: str, destination_path: str) -> str:
    """
    Moves a file or directory on the remote FTP server.

    :param session_id: The unique ID of the active session.
    :param source_path: The path to the file or directory to move.
    :param destination_path: The destination path.
    :return: A success message.
    """
    ftp = _check_session(session_id)
    try:
        ftp.rename(source_path, destination_path)
        logger.info(f"Moved '{source_path}' to '{destination_path}' for session '{session_id}'.")
        return f"Successfully moved '{source_path}' to '{destination_path}'."
    except Exception as e:
        logger.exception(f"Error moving '{source_path}' to '{destination_path}' for session '{session_id}'.")
        raise ToolError(f"Error moving '{source_path}': {e}")

def ftp_copy_recursive(session_id: str, source_path: str, destination_path: str) -> str:
    """
    Recursively copies a file or directory on the remote FTP server.

    :param session_id: The unique ID of the active session.
    :param source_path: The path to the file or directory to copy.
    :param destination_path: The destination path.
    :return: A success message.
    """
    ftp = _check_session(session_id)
    try:
        # Check if the source path is a directory or a file
        try:
            original_cwd = ftp.pwd()
            ftp.cwd(source_path)
            is_directory = True
            ftp.cwd(original_cwd)
        except error_perm:
            is_directory = False

        if is_directory:
            # It's a directory, so we need to create the destination directory and then recursively copy its contents
            try:
                ftp.mkd(destination_path)
            except error_perm as e:
                if "550" not in str(e): # Directory may already exist
                    raise
            
            for name, attrs in ftp.mlsd(path=source_path):
                if name not in ('.', '..'):
                    ftp_copy_recursive(session_id, f"{source_path}/{name}", f"{destination_path}/{name}")
            logger.info(f"Recursively copied directory '{source_path}' to '{destination_path}' for session '{session_id}'.")
        else:
            # It's a file, so we can just download it and then upload it to the destination
            in_memory_file = io.BytesIO()
            ftp.retrbinary(f"RETR {source_path}", in_memory_file.write)
            in_memory_file.seek(0)
            ftp.storbinary(f"STOR {destination_path}", in_memory_file)
            logger.info(f"Copied file '{source_path}' to '{destination_path}' for session '{session_id}'.")

        return f"Successfully copied '{source_path}' to '{destination_path}'."
    except Exception as e:
        logger.exception(f"Error copying '{source_path}' to '{destination_path}' for session '{session_id}'.")
        raise ToolError(f"Error copying '{source_path}': {e}")

def ftp_cd(session_id: str, directory: str) -> str:
    """
    Changes the current working directory on the remote FTP server.

    :param session_id: The unique ID of the active session.
    :param directory: The path to the new directory.
    :return: A success or error message.
    """
    ftp = _check_session(session_id)
    try:
        ftp.cwd(directory)
        new_cwd = ftp.pwd()
        logger.info(f"Changed directory to '{new_cwd}' for session '{session_id}'.")
        return f"Successfully changed directory to '{new_cwd}'."
    except all_errors as e:
        logger.exception(f"Error changing directory to '{directory}' for session '{session_id}'.")
        raise ToolError(f"Error changing directory: {e}")
