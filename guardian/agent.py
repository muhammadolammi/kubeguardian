
from google.adk.agents import Agent, SequentialAgent
from .prompts import observer_prompt, rca_prompt, remediator_prompt, orchestrator_prompt, chat_agent_prompt
from tools.toolset import  kubectl_ai_mcp_toolset,custom_mcp_toolset, email_mcp_tool
   



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

# def nake_file_system_Agent():
#     return Agent(
#         name="fs_agent",
#         model="gemini-2.0-flash",
#         description="File System agent for fs.",
#         instruction=remediator_prompt(),
#         output_key="fs_output",
#         tools=[]
#     )

def get_orchestrator_agent():
    return Agent(
        name="orchestrator_agent",
        description="Coordinates Observer, RCA, and Remediator agents for self-healing operations.",
        instruction=orchestrator_prompt(),
        sub_agents=[
            make_observer_agent(),
            make_rca_agent(),
            make_remediator_agent()
        ],
        tools=[kubectl_ai_mcp_toolset],
        model="gemini-2.5-flash",
        output_key= "orchestrator_response"
    )


def get_chat_agent():
    return Agent(
        name="chat_agent",
        description="Conversational entry point for Kubernetes operations, delegating to orchestrator and tools.",
        instruction=chat_agent_prompt(),
        sub_agents=[
            get_orchestrator_agent(),
        ],
        tools=[custom_mcp_toolset],
        model="gemini-2.5-flash",
        output_key="chat_response"
    )
root_agent = get_chat_agent()
# root_agent = Agent(
#     name="root_agent",
#     instruction="You are kubectl ai wrapper, you can do everything kubectl can do using natural language",
#     tools=[kubectl_ai_mcp_toolset],
#     model="gemini-2.5-flash",
# )

