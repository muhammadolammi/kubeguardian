from const import get_ENV
db_url = get_ENV("DB_URL")
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types  # For message parts
from const import APP_NAME




session_service = DatabaseSessionService(db_url=db_url)

def get_runner(root_agent: Agent) -> Runner:
    """Return a Runner tied to a specific session service."""
    return Runner(
        agent=root_agent,
        app_name=APP_NAME, 
        session_service=session_service
    )

async def call_agent_async(
    runner: Runner,
    user_id: str,
    session_id: str,
    message: str,
) -> str:
    """
    Executes the agent and returns its final response for the given session.
    Retries on RESOURCE_EXHAUSTED with a delay.
    """
    final_response_text = "Agent did not produce a final response."

    try:
        # Prepare the event message
        new_message = types.Content(
            role="user",
            parts=[types.Part(text=message)]
        )

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=new_message
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response_text = event.content.parts[0].text
                elif getattr(event, "actions", None) and getattr(event.actions, "escalate", False):
                    final_response_text = f"Agent escalated: {event.error_message or 'No message'}"
                return final_response_text  # ✅ done, return early
    except Exception as e:
        return f"⚠️ Agent failed to process your request: {str(e)}"
    return final_response_text




async def run(agent : Agent,session_data:dict,  message:str, ):
    """
    Main entrypoint: Creates a new session, runs the agent, and tears down cleanly.
    Each call to `run()` starts a new isolated session.
    """
    runner = get_runner(agent)
    #TODO make session creation time base, this shoould be an arg and not created here.
    #TODO new session every ten minute , or new session for each stream.
    user_id, session_id = session_data["user_id"], session_data["session_id"]
    try:
        response = await call_agent_async(runner, user_id, session_id, message)
        return response
    except Exception as e:
            return f"⚠️ Agent failed to process your request: {str(e)}"


