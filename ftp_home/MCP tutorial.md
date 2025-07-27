

## **Enhance Your Gemini CLI with Custom Local Tools**

You can significantly extend the capabilities of your Gemini CLI by creating and adding a local Model Context Protocol (MCP) server. This allows you to integrate your own custom tools, scripts, and data sources directly into Gemini's workflow. Here's a step-by-step guide to get you started.

### **Understanding the Model Context Protocol (MCP)**

The **Model Context Protocol (MCP)** is an open standard that enables AI systems like the Gemini CLI to communicate with external tools and data sources. An MCP server exposes a set of tools that the Gemini CLI can then utilize to perform a wider range of tasks. This could include interacting with your local databases, accessing specific APIs, or running custom scripts.

The communication between the Gemini CLI (the "host") and your local MCP server happens over a defined protocol, typically using standard input/output (stdio) for local servers.

---

### **Step 1: Prerequisites**

Before you begin, ensure you have the following installed on your system:

* **Node.js and npm:** The Gemini CLI itself is a Node.js application. You can download and install them from the official [Node.js website](https://nodejs.org/).  
* **Gemini CLI:** If you haven't already, install the Gemini CLI globally using npm:  
  Bash  
  npm install \-g @google/gemini-cli

* **A Programming Language for Your Server:** You can build your MCP server in various languages. This guide will provide examples for **Python** and **Node.js**, which are popular choices with readily available SDKs.  
* **Docker (Optional but Recommended):** For some pre-built MCP servers or for containerizing your own, having Docker installed is beneficial.

---

### **Step 2: Creating Your First Custom MCP Server**

The most effective way to add custom tools is to build a simple MCP server. Here’s how you can do this using either Python or Node.js.

#### **Option A: Building a "Hello, World\!" MCP Server with Python**

1. **Set up your project environment:**  
   Bash  
   mkdir my-python-mcp-server  
   cd my-python-mcp-server  
   python3 \-m venv .venv  
   source .venv/bin/activate  
   pip install "mcp\[cli\]"

2. **Create your server script:** Create a file named server.py and add the following code:  
   Python  
   from mcp.server.fastmcp import FastMCP

   \# Initialize the MCP server  
   mcp \= FastMCP("MyPythonServer")

   @mcp.tool()  
   def greet(name: str) \-\> str:  
       """  
       A simple tool that returns a greeting.

       :param name: The name of the person to greet.  
       :return: A personalized greeting.  
       """  
       return f"Hello, {name}\! This is your custom Python tool."

   if \_\_name\_\_ \== "\_\_main\_\_":  
       mcp.run()

   This script uses the mcp Python SDK to create a server with a single tool named greet.

#### **Option B: Building a "Hello, World\!" MCP Server with Node.js**

1. **Set up your project environment:**  
   Bash  
   mkdir my-node-mcp-server  
   cd my-node-mcp-server  
   npm init \-y  
   npm install @modelcontextprotocol/sdk zod

2. **Create your server script:** Create a file named index.js and add the following code:  
   JavaScript  
   import { McpServer, StdioServerTransport } from '@modelcontextprotocol/sdk/server';  
   import { z } from 'zod';

   // Initialize the MCP server  
   const server \= new McpServer({  
     name: 'MyNodeServer',  
     version: '1.0.0',  
   });

   // Define a tool  
   server.tool(  
     'greet',  
     'A simple tool that returns a greeting.',  
     {  
       input: z.object({  
         name: z.string().describe('The name of the person to greet.'),  
       }),  
       output: z.string(),  
     },  
     async (input) \=\> {  
       return \`Hello, ${input.name}\! This is your custom Node.js tool.\`;  
     }  
   );

   // Start the server with stdio transport  
   const transport \= new StdioServerTransport(server);  
   transport.listen();

   This Node.js script uses the @modelcontextprotocol/sdk to achieve the same result as the Python version.

---

### **Step 3: Configuring Gemini CLI to Use Your Local Server**

Now that you have a running MCP server, you need to tell the Gemini CLI how to find and use it.

1. **Locate your Gemini settings file:** The configuration for the Gemini CLI is stored in a file named settings.json. You can find it in your home directory within the .gemini folder (\~/.gemini/settings.json). If this file or folder doesn't exist, you can create them.  
2. **Edit the settings.json file:** Open the settings.json file in a text editor and add the mcpServers object. The configuration will differ slightly depending on whether you created a Python or Node.js server.  
   * **For the Python Server:**  
     JSON  
     {  
       "mcpServers": {  
         "my-python-tool-server": {  
           "command": "python3",  
           "args": \["/path/to/your/my-python-mcp-server/server.py"\],  
           "type": "stdio"  
         }  
       }  
     }

     **Important:** Replace /path/to/your/my-python-mcp-server/server.py with the absolute path to your server.py file.  
   * **For the Node.js Server:**  
     JSON  
     {  
       "mcpServers": {  
         "my-node-tool-server": {  
           "command": "node",  
           "args": \["/path/to/your/my-node-mcp-server/index.js"\],  
           "type": "stdio"  
         }  
       }  
     }

     **Important:** Replace /path/to/your/my-node-mcp-server/index.js with the absolute path to your index.js file.

---

### **Step 4: Interacting with Your Custom Tool**

With your MCP server running and the Gemini CLI configured, you can now use your new tool.

1. **Start the Gemini CLI:** Open a new terminal and run:  
   Bash  
   gemini

2. **Verify the MCP Server Connection:** Once inside the Gemini CLI, you can check if your local server is recognized by typing:  
   /mcp

   You should see your server listed (e.g., my-python-tool-server or my-node-tool-server).  
3. **Use your custom tool:** Now, you can invoke your greet tool with a natural language prompt:greet John Doe  
   The Gemini CLI will understand that this corresponds to your custom tool, execute the code in your local MCP server, and return the output.

By following these steps, you can create a variety of custom tools to enhance your Gemini CLI, making it a more powerful and personalized assistant for your specific development workflows.