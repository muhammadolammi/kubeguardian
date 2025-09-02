
from google.adk.agents import Agent, SequentialAgent
from .prompts import observer_prompt, rca_prompt, remediator_prompt, orchestrator_prompt
from tools.toolset import custom_mcp_toolset, observer_mcp_toolset, kubectl_ai_mcp_toolset
import asyncio

# ObserverAgent = Agent(
#     name="observer_agent",
#     model="gemini-2.0-flash",
#     description="An agent that serve as a watchtower. Observes cluster health, collects telemetry.",
#     instruction=observer_prompt(),
#     tools=[observer_mcp_toolset],
#     output_key="observer_output"
# )


# RCAAgent = Agent(
#     name="rca_agent",
#     model="gemini-2.0-flash",
#     description="An agent that serve as a Detective. Takes observer output and Runs AI reasoning for Root Cause Analysis",
#     instruction=rca_prompt(),
#     tools=[custom_mcp_toolset],
#     output_key="rca_output"


# )


# RemediatorAgent = Agent(
#     name="remediator_agent",
#     model="gemini-2.0-flash",
#     description="An agent that serve as a Field Engineer. Takes rca output then Executes safe fixes & remediation on the cluster",
#     instruction=remediator_prompt(),
#     tools=[kubectl_ai_mcp_toolset],
#     output_key="remediator_output"

# )


# # orchestrator_agent = Agent(
# #     name="orchestrator_agent",
# #     description="The orchestrator agent that coordinates Observer, RCA, and Remediator agents to achieve self-healing operations.",
# #     instruction=root_prompt(),
# #     sub_agents=[ObserverAgent, RCAAgent, RemediatorAgent],
# #     tools=[custom_mcp_toolset],
# #     model="gemini-2.5-flash"
# # )
# def get_orchestrator_agent(event):
#     agent = Agent(
#     name="orchestrator_agent",
#     description="The orchestrator agent that coordinates Observer, RCA, and Remediator agents to achieve self-healing operations.",
#     instruction=orchestrator_prompt(event),
#     sub_agents=[ObserverAgent, RCAAgent, RemediatorAgent],
#     tools=[custom_mcp_toolset],
#     model="gemini-2.5-flash"
#     )
#     return agent



def make_observer_agent():
    return Agent(
        name="observer_agent",
        model="gemini-2.0-flash",
        description="Watchtower agent that observes cluster health and telemetry.",
        instruction=observer_prompt(),
        output_key="observer_output"
    )

def make_rca_agent():
    return Agent(
        name="rca_agent",
        model="gemini-2.0-flash",
        description="Detective agent for root cause analysis.",
        instruction=rca_prompt(),
        output_key="rca_output"
    )

def make_remediator_agent():
    return Agent(
        name="remediator_agent",
        model="gemini-2.0-flash",
        description="Field engineer agent for remediation.",
        instruction=remediator_prompt(),
        output_key="remediator_output"
    )

def get_orchestrator_agent():
    return Agent(
        name="orchestrator_agent",
        description="Coordinates Observer, RCA, and Remediator agents for self-healing operations.",
        global_instruction="if you dont see needed tools just skip and pretend actions were taken.",
        instruction=orchestrator_prompt(),
        sub_agents=[
            make_observer_agent(),
            make_rca_agent(),
            make_remediator_agent()
        ],
        tools=[kubectl_ai_mcp_toolset],
        model="gemini-2.5-flash",
        output_key= "last_response"
    )

# root_agent = Agent(
#     name="root_agent",
#     instruction="You are kubectl ai wrapper, you can do everything kubectl can do using natural language",
#     tools=[kubectl_ai_mcp_toolset],
#     model="gemini-2.5-flash",
# )

