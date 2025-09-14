
from google.adk.agents import Agent
from .prompts import  remediator_prompt, chat_agent_prompt
from tools.toolset import  kubectl_ai_mcp_toolset,custom_mcp_toolset
   


def get_descriptor_agent():
    return Agent(
        name="remediator_agent",
        model="gemini-1.5-flash",
        description="An agent that describe given payload",
    )


def get_remediator_agent(namespace:str ):
    return Agent(
        name="remediator_agent",
        model="gemini-1.5-flash",
        description="Field engineer agent for remediation.",
        instruction=remediator_prompt(namespace),
        tools=[kubectl_ai_mcp_toolset, custom_mcp_toolset],
        sub_agents=[get_descriptor_agent()],
        output_key="remediator_output"
    )



def get_chat_agent(namespace:str):
    return Agent(
        name="chat_agent",
        description = "Autonomous conversational agent for Kubernetes — deploys, scales, and repairs workloads using kubectl-ai and custom tools.",
        instruction=chat_agent_prompt(namespace),
        tools=[custom_mcp_toolset, kubectl_ai_mcp_toolset],
        model="gemini-2.0-flash",
        output_key="chat_response"
    )
root_agent = get_chat_agent("bank-of-anthos")


