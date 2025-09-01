

from google.adk.agents import Agent


from toolset import kubectl_ai_mcp_toolset

remediator_agent = Agent(
    name="remediator_agent",
    model="gemini-2.0-flash",
    description="An agent that serve as a Field Engineer. Takes rca output then Executes safe fixes & remediation on the cluster",
    # instruction="I can answer your questions about the time and weather in a city.",
    tools=[kubectl_ai_mcp_toolset]
)