# My Python MCP Server

This project contains two main components:
1.  A standalone FTP server.
2.  An MCP (Multi-purpose Cooperative Protocol) server with FTP client capabilities.

## Prerequisites

- Python 3.7+
- pip (Python package installer)

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
    A `requirements.txt` file is not provided, but based on the code, you'll need the following packages. You can install them using pip:
    ```bash
    pip install pyftpdlib "mcp.py[server]"
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

1.  Start the FTP server and the MCP server in separate terminals as described above.
2.  In the Gemini CLI, use the `/mcp` command to connect to your running MCP server:
    ```
    /mcp connect localhost:8765
    ```
3.  Once connected, Gemini will have access to the tools defined in `server.py`. You can then instruct Gemini to use them.

    **Example Workflow:**

    -   **You:** `Connect to the FTP server.`
    -   **Gemini (using the tool):** `[tool_code: ftp_connect(server="127.0.0.1", port=2121, user="user", password="12345")]`

    -   **You:** `List the files on the FTP server.`
    -   **Gemini (using the tool):** `[tool_code: ftp_list()]`

    -   **You:** `Please upload "my_local_file.txt" to the server as "remote_copy.txt".`
    -   **Gemini (using the tool):** `[tool_code: ftp_put(local_path="my_local_file.txt", remote_path="remote_copy.txt")]`

### General Usage

1.  Start the FTP server in one terminal.
2.  Start the MCP server in another terminal.
3.  Connect to the MCP server using an MCP client (like Gemini).
4.  From the client, you can now use the `ftp_` tools to connect to and interact with your running FTP server.
    -   Example: Use `ftp_connect` with `server="127.0.0.1"`, `port=2121`, `user="user"`, and `password="12345"`.
    -   Then, you can use `ftp_list`, `ftp_get`, `ftp_put`, etc.