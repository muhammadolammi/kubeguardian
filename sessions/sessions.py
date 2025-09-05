

import uuid
from google.adk.sessions import InMemorySessionService
from const import APP_NAME
from const import logger

async def create_new_session(session_service: InMemorySessionService, user_id:str ):
    """
    Create a new session with a unique session ID.
    """
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    initial_state = {
        
    }

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
        state=initial_state
    )
    logger.info(f"✅ Created new session: {session_id}")
    return  session_id
