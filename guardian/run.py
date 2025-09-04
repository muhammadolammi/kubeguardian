
import uuid
import logging
import warnings
import asyncio

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types  # For message parts
from const import APP_NAME

# Ignore warnings and set logging
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_runner(root_agent: Agent, session_service: InMemorySessionService ) -> Runner:
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
    output_key: str,
    max_retries: int = 3,
) -> str:
    """
    Executes the agent and returns its final response for the given session.
    Retries on RESOURCE_EXHAUSTED with a delay.
    """
    attempt = 0
    final_response_text = "Agent did not produce a final response."

    while attempt <= max_retries:
        try:
            # Prepare the event message
            new_message = types.Content(
                role="user",
                parts=[types.Part(text=message)]
            )

            logger.info(f"🔹 Running agent (attempt {attempt+1}) for user: {user_id}, session: {session_id}")

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
            if "RESOURCE_EXHAUSTED" in str(e) and attempt < max_retries:
                delay = 25 * (attempt + 1)  # ⏱ exponential-ish backoff
                logger.warning(f"⚠️ Quota hit, retrying in {delay}s (attempt {attempt+1}/{max_retries})...")
                await asyncio.sleep(delay)
                attempt += 1
                continue
            else:
                logger.error(f"❌ Agent execution failed: {e}", exc_info=True)
                return f"⚠️ Agent failed to process your request: {str(e)}"

        # If loop finishes without final_response
        break

    logger.info(f"✅ Agent Response: {final_response_text}")
    return final_response_text




async def run(agent : Agent,session_service:InMemorySessionService,session_data:dict,  message:str, output_key:str):
    """
    Main entrypoint: Creates a new session, runs the agent, and tears down cleanly.
    Each call to `run()` starts a new isolated session.
    """
    runner = get_runner(agent,session_service)
    #TODO make session creation time base, this shoould be an arg and not created here.
    #TODO new session every ten minute , or new session for each stream.
    user_id, session_id = session_data["user_id"], session_data["session_id"]

    try:
        response = await call_agent_async(runner, user_id, session_id, message, output_key)
        return response
    except Exception as e:
        
        logger.error(f"❌ Agent run failed: {e}")
        return f"⚠️ Agent failed to process your request: {str(e)}"
    finally:
        logger.info(f"🧹 Session {session_id} complete.")


