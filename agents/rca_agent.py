

from google.adk.agents import Agent

from toolset import custom_mcp_toolset



rca_agent = Agent(
    name="rca_agent",
    model="gemini-2.0-flash",
    description="An agent that serve as a rca.",
    # instruction="I can answer your questions about the time and weather in a city.",
    tools=[custom_mcp_toolset]

)