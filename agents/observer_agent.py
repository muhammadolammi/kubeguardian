

from google.adk.agents import Agent

from toolset import custom_mcp_toolset


observer_agent = Agent(
    name="observer_agent",
    model="gemini-2.0-flash",
    description="An agent that serve as a observer.",
    # instruction="I can answer your questions about the time and weather in a city.",
    tools=[custom_mcp_toolset]
)