

from google.adk.agents import Agent

from toolset import observer_mcp_toolset
from prompts import observer_prompt


observer_agent = Agent(
    name="observer_agent",
    model="gemini-2.0-flash",
    description="An agent that serve as a watchtower. Observes cluster health, collects telemetry.",
    instruction=observer_prompt(),
    tools=[observer_mcp_toolset]
)