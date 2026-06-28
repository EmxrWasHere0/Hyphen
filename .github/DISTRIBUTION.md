# Hyphen Module Distribution

Hyphen supports two primary methods for expanding its capabilities through skills and tools.

* **`FunctionTool` (Google ADK):** Used for native, Python-based custom functions.
* **`mcp` Library:** Used for integrating Model Context Protocol (MCP) servers.

> [!WARNING]
> Other skill methods have not been tested on Hyphen. If you choose to implement alternative methods, you may encounter unverified bugs and will need to handle troubleshooting independently.

---

## 1. FunctionTool

The `FunctionTool` (`google.adk.tools.function_tool.FunctionTool`) allows you to expose raw Python functions directly to your agent as executable tools.

### Core Use Cases

* **OS & System Management** (e.g., Hyphen's native `execute_cmd`, `screenshot_wayland`, `press_key` modules)
* **Local Automation** (e.g., file manipulation, app interaction, hardware control)
* **Web Scraping & APIs** (fetching real-time data from web sources)
* **Ethical Hacking / Script Execution**

### Step-by-Step Implementation

1. **Define your core Python function:**
```python
import datetime

def get_current_time():
    """Returns the current system date and time."""
    return datetime.datetime.now()

```


2. **Register the tool inside the Hyphen Agent:**
```python
from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool

root_agent = Agent(
    # ... other agent configs ...
    tools=[
        FunctionTool(get_current_time)
    ]
)

```



### Execution Flow

```
User   --> "What's the date of today?"
Agent  --> Invokes tool: get_current_time()
Output --> 2026-06-28 08:06:37.12345
Agent  --> "Today is June 28, 2026. The time is 08:06 AM."
```

---

## 2. Python MCP (Model Context Protocol) Library

The `mcp` library enables Hyphen to interface with standard MCP Servers, making it highly extensible with ecosystem-wide tools. Hyphen's `filesystem` module relies completely on this protocol.

### Core Use Cases

* **Cross-platform Applications Control**
* **Database & Vector Store Integrations**
* **Advanced Context Management & Enterprise Tooling**

### Step-by-Step Implementation

1. **Environment Setup:**
Ensure the `mcp` library is installed inside your virtual environment. If you installed Hyphen via `HyInstaller`, verify its presence:
```fish
pip install mcp
pip show mcp
```


2. **Configure the MCP Toolset:**
Define your connection parameters to communicate with the target MCP server (e.g., the standard Node-based filesystem server):
```python
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

filesystem_access = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=[
                '-y',
                '@modelcontextprotocol/server-filesystem',
                "/path/to/target/directory",
            ],
        ),
    ),
)

```


3. **Inject the MCP Tool into the Agent:**
```python
root_agent = Agent(
    # ... other agent configs ...
    tools=[
        filesystem_access
    ]
)

```
### Execution Flow

```
User   --> "Can you review test.py?"
Agent  --> Explores directory via MCP: filesystem_access -> List Directory
Server --> Returns file list: ["test.py", "README.md"]
Agent  --> Reads file content via MCP: filesystem_access -> Read File "test.py"
Server --> Returns: "from a import b..."
Agent  --> "All code is clear. Good work!"
```
# 📦 Distributing Modules

Distributing your custom MCP Servers or Python functions as a Hyphen Module (`.hmp`) is a straightforward process.

> [!NOTE]
> This section covers module packaging, installation, and repository management for the Hyphen ecosystem.

---

## 🛠️ 1. Creating Modules

To build a module, you need a dedicated directory containing exactly two core files:

1. **`meta.hyphen`**: Contains metadata and entry points (uses YAML syntax).
2. **`my_module.py`**: Contains the actual Python functions or MCP configurations.

### File Templates

* **`meta.hyphen`**
```yaml
name: My Module
description: My First Hyphen Module
version: 1.0
authors:
  - name: Alex
    email: alex@example.com
  - name: Suzan
    email: suzan@example.com
file: my_module.py

```


* **`my_module.py`**
```python
def main(name: str):
    """Greets the given name."""
    return f"Hello, {name}!"

```



### Packaging & Local Testing

Once your files are ready, use the `hyphenctl` CLI utility to compile, test, and manage your module:

```fish
# Compile the files into a Hyphen Module Package (.hmp)
hyphenctl create /path/to/the/files/

# Expected output: /path/to/the/files/my_module.hmp

# Load and test the compiled package locally
hyphenctl load /path/to/the/files/my_module.hmp

# Remove the local test module when finished
hyphenctl remove my_module

```

---

## 🚀 2. Publishing Modules

Hyphen modules can be hosted and distributed across three different channel types:

* **Hyphen Official Repository** (Verified and built-in)
* **Custom Third-Party Repositories** (Self-hosted metadata databases)
* **Git Repositories** (Direct source code extraction)

> [!WARNING]
> Always review the source code of modules installed from outside the Hyphen Official Repository. If the raw source code isn't publicly visible, you can unpack/decompile any `.hmp` package using:
> `hyphenctl revert module_name /path/to/target`

---

## 📥 3. Installing Modules

### From Official Repository

```sh
hyphenctl install module_name
```

### From Custom Repositories

Add the third-party database endpoint before installing. If a custom package name conflicts with an official one, prefix it with the repository namespace:

```sh
# Add the custom database source
hyphenctl databases add https://example.com/hyphen/database

# Install the package (uses namespacing if names collide)
hyphenctl install custom_repo_module
```

### From Git Repositories

You can pull and install modules directly from a public Git repository:

```sh
hyphenctl git https://github.com/example/github_module_name
```

---

## 🔄 4. Updating & Removing

To sync with all configured repositories and pull the latest versions of your installed modules:

```sh
hyphenctl update
```

To clean up and completely remove an installed module from your system:

```sh
hyphenctl remove module_name
```