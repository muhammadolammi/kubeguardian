
from google.adk.agents import Agent
from .prompts import  remediator_prompt, chat_agent_prompt
from tools.toolset import  kubectl_ai_mcp_toolset,custom_mcp_toolset
   





def get_remediator_agent(namespace:str, ):
    return Agent(
        name="remediator_agent",
        model="gemini-2.0-flash",
        description="Field engineer agent for remediation.",
        instruction=remediator_prompt(namespace),
        tools=[kubectl_ai_mcp_toolset, custom_mcp_toolset],
        output_key="remediator_output"
    )

# def get_orchestrator_agent(namespace:str):
#     return Agent(
#         name="orchestrator_agent",
#         description="Coordinates Observer, RCA, and Remediator agents for self-healing operations.",
#         instruction=orchestrator_prompt(namespace),
#         sub_agents=[
#             make_rca_agent(),
#             make_remediator_agent(namespace)
#         ],
#         model="gemini-2.0-flash",
#         output_key= "orchestrator_response"
#     )


def get_chat_agent(namespace:str):
    return Agent(
        name="chat_agent",
        description = "Autonomous conversational agent for Kubernetes — deploys, scales, and repairs workloads using kubectl-ai and custom tools.",
        instruction=chat_agent_prompt(namespace),
        tools=[custom_mcp_toolset, kubectl_ai_mcp_toolset],
        model="gemini-2.0-flash",
        output_key="chat_response"
    )
root_agent = get_remediator_agent("main")
# root_agent = Agent(
#     name="root_agent",
#     instruction="You are kubectl ai wrapper, you can do everything kubectl can do using natural language",
#     tools=[kubectl_ai_mcp_toolset],
#     model="gemini-2.5-flash",
# )

