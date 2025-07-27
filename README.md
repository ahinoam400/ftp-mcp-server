# My Python MCP Server

This project contains two main components:
1.  A standalone FTP server.
2.  An MCP (Multi-purpose Cooperative Protocol) server with FTP client capabilities.

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

## Running the Servers

You must run the servers in separate terminal windows. Ensure your virtual environment is activated in each terminal.

### 1. Running the FTP Server

The FTP server provides a space for file storage and transfer. It runs on port `2121`.

-   **Start the server:**
    ```bash
    python ftp_server.py
    ```
-   The server will be running and listening for connections. The default user credentials are:
    -   **Username:** `user`
    -   **Password:** `12345`
-   The user's home directory is `ftp_home/`.

### 2. Running the MCP Server

The MCP server exposes several tools, including tools to interact with the FTP server. By default, it runs on `localhost:8765`.

-   **Start the server:**
    ```bash
    python server.py
    ```
-   The MCP server will start and be available for clients to connect to and use its tools.

## How to Use

### Connecting from the Gemini CLI

1.  **Start the FTP server and the MCP server in separate terminals as described above.**

2.  **Configure the Gemini CLI to use the local MCP server:**
    -   Locate your Gemini settings file. It's usually at `~/.gemini/settings.json` (for Linux/macOS) or `C:\Users\<YourUsername>\.gemini\settings.json` (for Windows).
    -   If the file or `.gemini` directory doesn't exist, create it.
    -   Open `settings.json` and add the following configuration. This tells Gemini how to start your local server.

    ```json
    {
      "mcpServers": {
        "my-python-ftp-server": {
          "command": "python",
          "args": ["/path/to/your/my-python-mcp-server/server.py"],
          "type": "stdio"
        }
      }
    }
    ```
    -   **CRITICAL:** You **must** replace `/path/to/your/my-python-mcp-server/server.py` with the correct **absolute path** to the `server.py` file on your system.

3.  **Start Gemini and connect:**
    -   Open a new terminal and run `gemini`.
    -   Inside the Gemini CLI, verify the connection with the `/mcp` command. You should see `my-python-ftp-server` in the list of available servers.

4.  **Interact with your tools:**
    Once connected, you can use natural language to invoke the tools from your `server.py` file.

    **Example Workflow:**

    -   **You:** `Connect to the FTP server.`
    -   **Gemini (using the tool):** `[tool_code: ftp_connect(server="127.0.0.1", port=2121, user="user", password="12345")]`

    -   **You:** `List the files on the FTP server.`
    -   **Gemini (using the tool):** `[tool_code: ftp_list()]`

    -   **You:** `Please upload "my_local_file.txt" to the server as "remote_copy.txt".`
    -   **Gemini (using the tool):** `[tool_code: ftp_put(local_path="my_local_file.txt", remote_path="remote_copy.txt")]`
