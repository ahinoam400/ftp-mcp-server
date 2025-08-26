import logging
from pathlib import Path

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