from const import get_ENV

namespace= get_ENV("AUTHORIZED_NAMESPACE")
mcp_server = get_ENV("MCP_SERVER")
print(mcp_server)

from google.adk.agents import Agent
from prompts import  chat_agent_prompt
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams


mcp_toolset = MCPToolset(
    connection_params=SseConnectionParams(
        url=mcp_server,
    ),
)  

root_agent= Agent(
        name="chat_agent",
        description = "Autonomous conversational agent for Kubernetes — deploys, scales, and repairs workloads using kubectl-ai and custom tools.",
        instruction=chat_agent_prompt(namespace),
        tools=[mcp_toolset],
        model="gemini-2.0-flash",
        output_key="chat_response"
    )