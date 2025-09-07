from const import get_ENV
db_url = get_ENV("DB_URL")

import uuid
from google.adk.sessions import DatabaseSessionService
# Example using a local SQLite file:

from const import APP_NAME
from const import logger


session_service = DatabaseSessionService(db_url=db_url)

async def create_new_session( user_id:str ):
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




async def get_session( session_id:str ):
    """
    Get  session with a session ID.
    """
    
    return session_service.get_session(session_id=session_id)




async def delete_session( session_id:str ):
    """
    Delete  session .
    """
    
    return session_service.delete_session(session_id=session_id)



