from const import get_ENV
from toolset import kubectl_ai_toolset,mcp_toolset
from prompts import  chat_agent_prompt
from google.adk.agents import Agent


namespace= get_ENV("AUTHORIZED_NAMESPACE")


root_agent= Agent(
        name="chat_agent",
        description = "Autonomous conversational agent for Kubernetes — deploys, scales, and repairs workloads using kubectl-ai and custom tools.",
        instruction=chat_agent_prompt(namespace),
        tools=[mcp_toolset, kubectl_ai_toolset],
        model="gemini-2.0-flash",
        output_key="chat_response"
    )