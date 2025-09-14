from const import get_ENV

namespace= get_ENV("AUTHORIZED_NAMESPACE")

from google.adk.agents import Agent
from prompts import  chat_agent_prompt
from tools.toolset import  kubectl_ai_mcp_toolset,custom_mcp_toolset
   

root_agent= Agent(
        name="chat_agent",
        description = "Autonomous conversational agent for Kubernetes — deploys, scales, and repairs workloads using kubectl-ai and custom tools.",
        instruction=chat_agent_prompt(namespace),
        tools=[custom_mcp_toolset, kubectl_ai_mcp_toolset],
        model="gemini-2.0-flash",
        output_key="chat_response"
    )