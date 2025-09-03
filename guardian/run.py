
import uuid
import logging
import warnings

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types  # For message parts

# Ignore warnings and set logging
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- App Constants ---
APP_NAME = "kubeguardian"
USER_ID = "kubeguardian"

def get_runner(root_agent: Agent, session_service: InMemorySessionService ) -> Runner:
    """Return a Runner tied to a specific session service."""
    return Runner(
        agent=root_agent,
        app_name=APP_NAME, 
        session_service=session_service
    )


async def call_agent_async( runner: Runner, user_id: str, session_id: str,payload):
    """
    Executes the agent and prints its final response for the given session.
    """
    final_response_text = "Agent did not produce a final response."
     # Prepare the event message for the agent
    new_message = types.Content(
        role="user",
        parts=[types.Part(text=payload)]
    )

    logger.info(f"🔹 Running agent for user: {user_id}, session: {session_id}")
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=new_message):
        # Uncomment to see all events:
        # logger.debug(f"Event: Author={event.author}, Final={event.is_final_response()}, Content={event.content}")

        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = f"Agent escalated: {event.error_message or 'No message'}"
            break

    logger.info(f"✅ Agent Response: {final_response_text}")
    return final_response_text


async def create_new_session(session_service: InMemorySessionService, ):
    """
    Create a new session with a unique session ID.
    """
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    user_id = USER_ID
    initial_state = {}

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
        state=initial_state
    )
    logger.info(f"✅ Created new session: {session_id}")
    return user_id, session_id


async def run(agent : Agent, payload):
    """
    Main entrypoint: Creates a new session, runs the agent, and tears down cleanly.
    Each call to `run()` starts a new isolated session.
    """
    session_service = InMemorySessionService()
    runner = get_runner(agent,session_service)
    #TODO make session creation time base, this shoould be an arg and not created here.
    #TODO new session every ten minute , or new session for each stream.
    user_id, session_id = await create_new_session(session_service)

    try:
        response = await call_agent_async(runner, user_id, session_id, payload)
        return response
    except Exception as e:
        logger.error(f"❌ Agent run failed: {e}")
        # raise
    finally:
        logger.info(f"🧹 Session {session_id} complete.")


