# My Python MCP Server

This project contains two main components:
1.  An MCP server with FTP client capabilities.
2.  A standalone FTP server.

## Prerequisites

- Python 3.7+
- pip (Python package installer)
- Node.js and npm (for the Gemini CLI)

## Setup

1.  **Clone the repository (or download the files):**
    ```bash
    git clone <repository-url>
    cd my-python-mcp-server
    ```

2.  **Create and activate a virtual environment:**

    -   **Windows:**
        ```bash
        python -m venv .venv
        .\.venv\Scripts\activate
        ```

    -   **Linux/macOS:**
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install the Gemini CLI:**
    ```bash
    npm install -g @google/gemini-cli
    ```





## How to Use

### Connecting from the Gemini CLI

1.  **Start the FTP server:**
    ```bash
    python ftp_server.py
    ```
-   The server will be running and listening for connections. The default user credentials are:
    -   **Username:** `user`
    -   **Password:** `12345`
-   The user's home directory is `ftp_home/`.

2.  **Configure the Gemini CLI to use the local MCP server:**

    To make the MCP server discoverable by the Gemini CLI, you need to configure it in the settings.json file. This file tells the Gemini CLI how to find and communicate with the MCP server.
    -   Locate your Gemini settings file. It's usually at `~/.gemini/settings.json` (for Linux/macOS) or `C:\Users\<YourUsername>\.gemini\settings.json` (for Windows).
    -   If the file or `.gemini` directory doesn't exist, create it.
    -   Open `settings.json` and add the following configuration. This tells Gemini how to start your local server.

    ```json
    {
      "mcpServers": {
        "my-python-ftp-server": {
          "command": "/path/to/your/my-python-mcp-server/.venv/Scripts/python.exe",
          "args": ["/path/to/your/my-python-mcp-server/server.py"],
          "type": "stdio"
        }
      }
    }
    ```
    

3.  **Start Gemini:**
    -   Open a new terminal and run `gemini`.
    -   Inside the Gemini CLI, verify the connection with the `/mcp` command. You should see `my-python-ftp-server` in the list of available servers.
    - Press Control+T to see details about each of the available tools.

4.  **Interact with your tools:**
    You can use natural language to invoke the tools.  
    To connect to the default FTP server, type in natural language "Connect to server". Gemini will find the username and password in this README.  
    

    **Example Workflow:**

    -   **You:** `Connect to the FTP server.`
    -   **Gemini (using the tool):** `[tool_code: ftp_connect(server="127.0.0.1", port=2121, user="user", password="12345")]`

    -   **You:** `List the files on the FTP server.`
    -   **Gemini (using the tool):** `[tool_code: ftp_list()]`

    -   **You:** `Please upload "my_local_file.txt" to the server as "remote_copy.txt".`
    -   **Gemini (using the tool):** `[tool_code: ftp_put(local_path="my_local_file.txt", remote_path="remote_copy.txt")]`

### Connecting to an External FTP Server

The MCP server is not limited to the local FTP server. You can connect to any FTP server by providing the correct details to the `ftp_connect` tool.

1.  **Start your own FTP server**

2. **Follow steps 2 and 3 above**
   

3.  **Use the `ftp_connect` tool with the external server's details.**

    **Example:**
    If you have a FTP server with the following credentials:
    -   **Host:** `ftp.example.com`
    -   **Username:** `myuser`
    -   **Password:** `mypassword123`

    You would ask Gemini to connect like this:

    -   **You:** `Connect to the ftp server at ftp.example.com with username myuser and password mypassword123`
    -   **Gemini (using the tool):** `[tool_code: ftp_connect(host="ftp.example.com", username="myuser", password="mypassword123")]`

    Once connected, you will receive a session ID and can use the other FTP tools (`ftp_list`, `ftp_get`, etc.) to interact with the remote server.
