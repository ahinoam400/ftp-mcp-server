import io
import re
import uuid
from ftplib import FTP, error_perm
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from ftp_logger import logger


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
        # A simple command to check whether the connection is still alive
        ftp.voidcmd('NOOP')
    except Exception:
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
        welcome_msg = ftp.getwelcome()
        return f"Successfully connected to the FTP server. Your session ID is: {session_id}.\n Server's Welcome message: {welcome_msg}"
    except Exception as e:
        logger.exception(f"Failed to connect to FTP server '{host}' with user '{username}'.")
        raise ToolError(f"Failed to connect to FTP server: {e}")


def ftp_disconnect(session_id: str) -> str:
    """
    Disconnects from the FTP server.
    
    :param session_id: The unique ID of the active session.
    :return: A success message.
    """
    ftp = ftp_sessions.get(session_id)
    if not ftp:
        return f"Session with ID '{session_id}' was not found or already disconnected."
    try:
        ftp.quit()
        del ftp_sessions[session_id]
        logger.info(f"Session '{session_id}' has been closed.")
        return f"Session '{session_id}' disconnected successfully."
    except Exception as e:
        logger.exception(f"Error while disconnecting session '{session_id}'.")
        raise ToolError(f"Error while disconnecting session '{session_id}': {e}")


def _ftp_list_by_method(list_method: str, session_id: str, directory: str) -> List[Union[str, Dict[str, Any]]]:
    """
    Lists the contents of a directory on a remote FTP server by the chosen list method
    Returns a list of the directory content according to the listing method.
    
    :param list_method: The ftp listing method
    :param session_id: The unique ID of the active session.
    :param directory: The directory to list. Defaults to the user's current directory.
    :return: A list of filenames in the specified directory.
    """
    ftp = _check_session(session_id)
    files_output = []
    try:
        original_cwd = ftp.pwd()

        ftp.cwd(directory)
        if "NLST" == list_method:
            files_output = ftp.nlst()
        elif "LIST" == list_method:
            ftp.retrlines(list_method, files_output.append)
        elif "MLSD" == list_method:
            if not hasattr(ftp, 'mlsd'):
                logger.exception(f"MLSD command not supported, failed executing for session '{session_id}'.")
                raise ToolError("MLSD command not supported by this FTP server or Python version.")
            raw_output = list(ftp.mlsd())
            files_output = [{"filename": filename, "attributes": attributes} for filename, attributes in raw_output]

        ftp.cwd(original_cwd)

        logger.info(f"{list_method}: Listed directory '{directory}' for session '{session_id}'.")
        return files_output
    except Exception as e:
        logger.exception(f"Error listing '{directory}' with the '{list_method}' command for session '{session_id}'.")
        raise ToolError(f"Error listing directory ({list_method}): {e}")


def ftp_nlst(session_id: str, directory: str = ".") -> List[str]:
    """
    Lists the contents of a directory on a remote FTP server using the NLST command.
    Returns a simple list of filenames.
    
    :param session_id: The unique ID of the active session.
    :param directory: The directory to list. Defaults to the user's current directory.
    :return: A list of filenames in the specified directory.
    """
    return _ftp_list_by_method("NLST", session_id, directory)


def ftp_list(session_id: str, directory: str = ".") -> List[str]:
    """
    Lists the contents of a directory on a remote FTP server using the LIST command.
    Returns a raw list of strings containing detailed file information.
    
    :param session_id: The unique ID of the active session.
    :param directory: The directory to list. Defaults to the user's current directory.
    :return: A list of raw strings with file details.
    """
    return _ftp_list_by_method("LIST", session_id, directory)


def ftp_mlsd(session_id: str, directory: str = ".") -> List[Dict[str, Any]]:
    """
    Lists the contents of a directory on a remote FTP server using the MLSD command.
    Returns a structured list of dictionaries, with each dictionary containing a 
    filename and its attributes.
    
    :param session_id: The unique ID of the active session.
    :param directory: The directory to list. Defaults to the user's current directory.
    :return: A structured list of dictionaries with file information.
    """
    return _ftp_list_by_method("MLSD", session_id, directory)


def ftp_retrieve_file(session_id: str, filename: str) -> str:
    """
    Retrieves a file from a FTP server using an active session.

    :param session_id: The unique ID of the active session.
    :param filename: The name of the file to retrieve.
    :return: The content of the file as a string.
    """
    ftp = _check_session(session_id)
    content_list = []

    try:
        ftp.retrbinary(f"RETR {filename}", content_list.append)
        content = b"".join(content_list).decode("utf-8")
        logger.info(f"Retrieved content of '{filename}' for session '{session_id}'.")
        return content
    except Exception as e:
        logger.exception(f"Error retrieving file '{filename}' for session '{session_id}'.")
        raise ToolError(f"Error retrieving file content: {e}")

def _ftp_store_methods_helper(session_id: str, is_unique_store: bool, local_filepath: str, 
                              remote_filename: Optional[str] = None) -> str:
    """
    Uploads a local file to a remote FTP server using an active session.
    
    :param session_id: The unique ID of the active session.
    :param is_unique_store: Is the store method is 'STOU'
    :param local_filepath: The path to the local file to upload.
    :param remote_filename: The name to save the file as on the server. If None, uses the local filename.
    :return: A success message.
    """
    ftp = _check_session(session_id)

    error_message = f"Error uploading '{local_filepath}' to session '{session_id}'."

    if not Path(local_filepath).exists():
        logger.exception(error_message)
        raise ToolError(f"Local file not found: {local_filepath}")

    try:
        with open(local_filepath, 'rb') as f:
            if is_unique_store:
                # Send STOU command and parse the unique filename from the server's response
                stou_command = f"STOU {Path(local_filepath).name}" # Suggest a name, server will make it unique
                server_response = ftp.sendcmd(stou_command)
                # Expected response: 150 FILE: <filename>
                match = re.search(r'FILE: (.+)', server_response)
                if not match:
                    raise ToolError(f"Failed to parse unique filename from STOU response: {server_response}")
                unique_filename = match.group(1).strip()

                # Upload the file using the unique filename provided by the server
                ftp.storbinary(f"STOR {unique_filename}", f)
                logger.info(f"Uploaded '{local_filepath}' to '{unique_filename}' for session '{session_id}'.")
                return f"File uploaded successfully with unique name: {unique_filename}"
            else:
                remote_filename = remote_filename or Path(local_filepath).name
                ftp.storbinary(f"STOR {remote_filename}", f)
                logger.info(f"Uploaded '{local_filepath}' to '{remote_filename}' for session '{session_id}'.")
                return f"File '{local_filepath}' uploaded successfully."
    except Exception as e:
        logger.exception(error_message)
        raise ToolError(f"Error uploading file: {e}")


def ftp_store_file(session_id: str, local_filepath: str, remote_filename: Optional[str] = None) -> str:
    """
    Uploads a local file to a remote FTP server using an active session. 
    If a file with that name already exists, it will be overwritten.
    
    :param session_id: The unique ID of the active session.
    :param local_filepath: The path to the local file to upload.
    :param remote_filename: The name to save the file as on the server. If None, uses the local filename.
    :return: A success message.
    """
    return _ftp_store_methods_helper(session_id, False, local_filepath, remote_filename)    

def ftp_store_file_unique(session_id: str, local_filepath: str) -> str:
    """
    Uploads a local file to the remote FTP server with a unique name generated by the server.
    
    :param session_id: The unique ID of the active session.
    :param local_filepath: The path to the local file to upload.
    :return: A success message that includes the unique filename assigned by the server.
    """
    return _ftp_store_methods_helper(session_id, True, local_filepath)

def ftp_rename(session_id: str, from_name: str, to_name: str) -> str:
    """
    Renames a file (or directory) on the remote FTP server.
    
    :param session_id: The unique ID of the active session.
    :param from_name: The current name of the file to be renamed.
    :param to_name: The new name for the file.
    :return: A success message.
    """
    ftp = _check_session(session_id)
    try:
        ftp.rename(from_name, to_name)
        logger.info(f"Renamed file from '{from_name}' to '{to_name}' for session '{session_id}'.")
        return f"Successfully renamed '{from_name}' to '{to_name}'."
    except Exception as e:
        logger.exception(f"Error renaming file from '{from_name}' to '{to_name}' for session '{session_id}'.")
        raise ToolError(f"Error renaming file: {e}")


def _is_dir(ftp: FTP, remote_path: str) -> bool:
    """
    Verifys if a given path on the FTP server is a directory.

    :param ftp_session: The ftp instance
    :param remote_path: The path to check
    :return: whether the given path is a directory
    """
    try:
        original_cwd = ftp.pwd()
        ftp.cwd(remote_path)
        ftp.cwd(original_cwd)
        return True
    except Exception:
        return False


def ftp_delete_recursive(session_id: str, remote_path: str) -> str:
    """
    Recursively deletes a file or directory on the remote FTP server.

    :param session_id: The unique ID of the active session.
    :param remote_path: The path to the file or directory to delete.
    :return: A success message.
    """
    ftp = _check_session(session_id)
    try:
        if _is_dir(ftp, remote_path):
            # It's a directory, so we need to recursively delete its contents
            for name, _ in ftp.mlsd(path=remote_path):
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
        if _is_dir(ftp, source_path):
            # It's a directory, we need to create the destination directory and then recursively copy its contents
            try:
                ftp.mkd(destination_path)
            except error_perm as e:
                if "550" not in str(e): # Directory may already exist
                    logger.exception(f"Error copying '{source_path}' to '{destination_path}' for session '{session_id}'.")
                    raise ToolError(f"Error copying '{source_path}', couldn't create the new directory: {e}")
            
            for name, _ in ftp.mlsd(path=source_path):
                if name not in ('.', '..'):
                    ftp_copy_recursive(session_id, f"{source_path}/{name}", f"{destination_path}/{name}")
            logger.info(f"Recursively copied directory '{source_path}' to '{destination_path}' for session '{session_id}'.")
        else:
            # It's a file, we can just download it and then upload it to the destination
            in_memory_file = io.BytesIO()
            ftp.retrbinary(f"RETR {source_path}", in_memory_file.write)
            in_memory_file.seek(0)
            ftp.storbinary(f"STOR {destination_path}", in_memory_file)
            logger.info(f"Copied file '{source_path}' to '{destination_path}' for session '{session_id}'.")
        
        return f"Successfully copied '{source_path}' to '{destination_path}'."
    except Exception as e:
        logger.exception(f"Error copying '{source_path}' to '{destination_path}' for session '{session_id}'.")
        raise ToolError(f"Error copying '{source_path}': {e}")


def ftp_cwd(session_id: str, directory: str) -> str:
    """
    Changes the current working directory on the remote FTP server.

    :param session_id: The unique ID of the active session.
    :param directory: The path to the new directory.
    :return: A success message.
    """
    ftp = _check_session(session_id)
    try:
        ftp.cwd(directory)
        new_cwd = ftp.pwd()
        logger.info(f"Changed directory to '{new_cwd}' for session '{session_id}'.")
        return f"Successfully changed directory to '{new_cwd}'."
    except Exception as e:
        logger.exception(f"Error changing directory to '{directory}' for session '{session_id}'.")
        raise ToolError(f"Error changing directory: {e}")


def ftp_pwd(session_id: str) -> str:
    """
    Prints the current working directory on the remote FTP server.
    
    :param session_id: The unique ID of the active session.
    :return: Aa success message containing the current directory name.
    """
    ftp = _check_session(session_id)
    try:
        current_dir = ftp.pwd()
        logger.info(f"PWD: Current directory for session '{session_id}' is '{current_dir}'.")
        return f"Current directory: {current_dir}"
    except Exception as e:
        logger.exception(f"Error getting current directory for session '{session_id}'.")
        raise ToolError(f"Error getting current directory: {e}")


def ftp_mkdir(session_id: str, directory_name: str) -> str:
    """
    Creates a new directory on the remote FTP server.
    
    :param session_id: The unique ID of the active session.
    :param directory_name: The name of the new directory to create.
    :return: A success message.
    """
    ftp = _check_session(session_id)
    try:
        ftp.mkd(directory_name)
        logger.info(f"Created directory '{directory_name}' for session '{session_id}'.")
        return f"Successfully created directory '{directory_name}'."
    except Exception as e:
        logger.exception(f"Error creating directory '{directory_name}' for session '{session_id}'.")
        raise ToolError(f"Error creating directory: {e}")
    

def ftp_rmdir(session_id: str, directory_name: str) -> str:
    """
    Removes a directory on the remote FTP server.
    
    :param session_id: The unique ID of the active session.
    :param directory_name: The name of the directory to remove.
    :return: A success message.
    """
    ftp = _check_session(session_id)
    try:
        ftp.rmd(directory_name)
        logger.info(f"Removed directory '{directory_name}' for session '{session_id}'.")
        return f"Successfully removed directory '{directory_name}'."
    except Exception as e:
        logger.exception(f"Error removing directory '{directory_name}' for session '{session_id}'.")
        raise ToolError(f"Error removing directory: {e}")


def ftp_abort_transfer(session_id: str) -> str:
    """
    Aborts the previous file transfer command.
    
    :param session_id: The unique ID of the active session.
    :return: A success message.
    """
    ftp = _check_session(session_id)
    try:
        ftp.abort()
        logger.info(f"Aborted previous command for session '{session_id}'.")
        return "Previous command aborted successfully."
    except Exception as e:
        logger.exception(f"Error aborting transfer for session '{session_id}'.")
        raise ToolError(f"Error aborting command: {e}")


def ftp_cdup_directory(session_id: str) -> str:
    """
    Changes the current working directory on the remote FTP server to the parent directory.

    :param session_id: The unique ID of the active session.
    :return: A success message.
    """
    ftp = _check_session(session_id)
    try:
        ftp.cwd("..")
        new_cwd = ftp.pwd()
        logger.info(f"Moved to parent directory for session '{session_id}'. New directory: {new_cwd}")
        return f"Successfully moved to parent directory. New directory: {new_cwd}"
    except Exception as e:
        logger.exception(f"Error changing to parent directory for session '{session_id}'.")
        raise ToolError(f"Error changing to parent directory: {e}")


def ftp_get_file_size(session_id: str, file_path: str) -> str:
    """
    Sends a 'SIZE' command to the server to get a file's size.
    
    :param session_id: The unique ID of the active session.
    :param file_path: The path to the file.
    :return: A success message containing the size of the file in bytes.
    """
    ftp = _check_session(session_id)
    try:
        # Ensure ASCII mode initially
        ftp.voidcmd('TYPE A')  

        # Set transfer type to binary for SIZE command
        ftp.voidcmd('TYPE I')
        size = ftp.size(file_path)
        
        # Restore ASCII mode after getting size
        ftp.voidcmd('TYPE A')

        logger.info(f"Size of '{file_path}' is {size} bytes.")
        return f"File size: {size} bytes."
    except Exception as e:
        logger.exception(f"Error recieving file size of '{file_path}' for session '{session_id}'.")
        raise ToolError(f"Failed to recieve file size: {e}")


def ftp_send_command(session_id: str, command: str) -> str:
    """
    Sends a raw command to the server and returns the response.
    This is the 'sendcmd' tool.
    
    :param session_id: The unique ID of the active session.
    :param command: The FTP command to send (e.g., 'SYST').
    :return: The server's response.
    """
    ftp = _check_session(session_id)
    try:
        response = ftp.sendcmd(command)
        logger.info(f"Sent command '{command}'. Response: {response}")
        return f"Raw response: {response}"
    except Exception as e:
        logger.exception(f"Error executing '{command}' for session '{session_id}'.")
        raise ToolError(f"Failed to send command '{command}': {e}")


def ftp_void_command(session_id: str, command: str) -> str:
    """
    Sends a raw command that is expected to return no data (a 'void' response).
    This is the 'voidcmd' tool.
    
    :param session_id: The unique ID of the active session.
    :param command: The FTP command to send (e.g., 'NOOP').
    :return: A success message.
    """
    ftp = _check_session(session_id)
    try:
        ftp.voidcmd(command)
        logger.info(f"Sent void command '{command}'.")
        return f"Command '{command}' sent successfully."
    except Exception as e:
        logger.exception(f"Error executing '{command}' for session '{session_id}'.")
        raise ToolError(f"Failed to send void command '{command}': {e}")    
