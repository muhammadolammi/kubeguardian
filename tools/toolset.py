from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

custom_mcp_toolset = MCPToolset(
             connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command='python',
                    args=[
                        "-m","mcp_server.server",
                    ],
                    env={},
                ),
            ),
            # Optional: Filter which tools from the MCP server are exposed
            #TODO add the neccasary tool needed eg DATADOG alert
            # tool_filter=['get_dev_name_tool', 'read_file']
            # timeout=30.0
        )


observer_mcp_toolset = MCPToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command='python',
                    args=[
                        "-m","mcp_server.server",
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
                    command='kubectl-ai',
                    args=[
                        "--mcp-server",
                    ],
                    env={},
                ),
            ),
            # Optional: Filter which tools from the MCP server are exposed
            #TODO add the neccasary tool needed eg DATADOG alert
            # tool_filter=['list_directory', 'read_file']
        )