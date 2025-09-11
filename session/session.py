from const import get_ENV
db_url = get_ENV("DB_URL")
import asyncio

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

    session=await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
        state=initial_state
    )
    logger.info(f"✅ Created new session: {session_id}")
    return  session




async def get_session( session_id:str, user_id:str ):
    """
    Get  session with a session ID.
    """
    
    return await session_service.get_session(session_id=session_id, app_name=APP_NAME, user_id=user_id)




async def delete_session( session_id:str, user_id:str, app_name:str ):
    """
    Delete  session .
    """
    
    await session_service.delete_session(session_id=session_id, user_id=user_id, app_name=app_name)







# async def main():
#     session = await get_session("session_6ef4a4b3", "remediator")
#     print(type(session))
#     print(session)




# asyncio.run(main())
