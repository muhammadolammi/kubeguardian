

from const import get_ENV
from prompts import  remediator_prompt
from toolset import kubectl_ai_toolset,mcp_toolset
from google.adk.agents import Agent



namespace= get_ENV("AUTHORIZED_NAMESPACE")


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
        tools=[mcp_toolset, kubectl_ai_toolset],
        sub_agents=[descriptor_agent],
        output_key="remediator_output"
    )



 
