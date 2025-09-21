

from const import get_ENV

from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams, StreamableHTTPConnectionParams

mcp_server = get_ENV("MCP_SERVER")
kubectl_ai_mcp_server = get_ENV("KUBECTL_AI_MCP_SERVER")


mcp_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=mcp_server,
    ),
)   

kubectl_ai_toolset = MCPToolset(
    connection_params= SseConnectionParams(
        url=kubectl_ai_mcp_server
    )
)
