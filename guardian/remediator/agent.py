

from const import get_ENV

namespace= get_ENV("AUTHORIZED_NAMESPACE")

from google.adk.agents import Agent
from prompts import  remediator_prompt
from tools.toolset import  kubectl_ai_mcp_toolset,custom_mcp_toolset
   


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
        tools=[kubectl_ai_mcp_toolset, custom_mcp_toolset],
        sub_agents=[descriptor_agent],
        output_key="remediator_output"
    )



 
