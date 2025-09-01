

from google.adk.agents import Agent

from toolset import custom_mcp_toolset


from prompts import rca_prompt
rca_agent = Agent(
    name="rca_agent",
    model="gemini-2.0-flash",
    description="An agent that serve as a Detective. Takes observer output and Runs AI reasoning for Root Cause Analysis",
    instruction=rca_prompt(),
    tools=[custom_mcp_toolset]

)