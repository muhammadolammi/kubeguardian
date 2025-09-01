from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
import os
TARGET_FOLDER_PATH = "./mcp_files"

custom_mcp_toolset = MCPToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command='npx',
                    args=[
                        "-y",  # Argument for npx to auto-confirm install
                        "./mcp/server.py",
 
                    ],
                    env={},
                ),
            ),
            # Optional: Filter which tools from the MCP server are exposed
            #TODO add the neccasary tool needed eg DATADOG alert
            # tool_filter=['list_directory', 'read_file']
        )


observer_mcp_toolset = MCPToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command='npx',
                    args=[
                        "-y",  # Argument for npx to auto-confirm install
                        "./mcp/server.py",
 
                    ],
                    env={},
                ),
            ),
            # Optional: Filter which tools from the MCP server are exposed
            #TODO add the neccasary tool needed eg DATADOG alert
            tool_filter=['Get_Metrics', ]
        )


kubectl_ai_mcp_toolset = MCPToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command='npx',
                    args=[
                        "-y",  # Argument for npx to auto-confirm install
                        "kubectl-ai --mcp-server",
                    ],
                    env={},
                ),
            ),
            # Optional: Filter which tools from the MCP server are exposed
            #TODO add the neccasary tool needed eg DATADOG alert
            # tool_filter=['list_directory', 'read_file']
        )