

from const import get_ENV

namespace= get_ENV("AUTHORIZED_NAMESPACE")
mcp_server = get_ENV("MCP_SERVER")


from google.adk.agents import Agent
from prompts import  remediator_prompt

from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams

mcp_toolset = MCPToolset(
    connection_params=SseConnectionParams(
        url=mcp_server,
    ),
)   


descriptor_agent= Agent(
        name="remediator_agent",
        model="gemini-2.0-flash",
        description="An agent that describe given payload",
    )


root_agent = Agent(
        name="remediator_agent",
        model="gemini-2.0-flash",
        description="Field engineer agent for remediation.",
        instruction=remediator_prompt(namespace),
        tools=[mcp_toolset],
        sub_agents=[descriptor_agent],
        output_key="remediator_output"
    )



 
