# Hyphen Core Engine (HyCore) Source File
# ADK Runtime version
#
# Google ADK is a product of Google LLC.
#
# Hyphen Project is licensed under GPLv3
#

import os
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import google_search
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

MODEL = f"{os.getenv("PROVIDER")}/{os.getenv("MODEL")}" # Model's full name (provider/model-name)

root_agent = Agent(
    name="assistant",
    model=LiteLlm(
        model=MODEL,
        api_key=os.getenv("API_KEY"), # API key's .env variable name
        base_url="" # API provider's base API URL
    ),
    instruction=f"", # Given instructions
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command='npx',
                    args=[
                        '-y',
                        '@modelcontextprotocol/server-filesystem',
                        "", # Allowed directory
                    ],
                ),
            ),
        ),
    ],
)