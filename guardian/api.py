from const import get_ENV
authorized_namespace = get_ENV("AUTHORIZED_NAMESPACE")


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

from guardian.agent import get_remediator_agent, get_chat_agent
from guardian.run import run

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="AI Agent Service", version="1.0")

# Request model
class AgentRequest(BaseModel):
    agent_type: str  # "remediator" or "chat"
    user_id: str
    session_id: str
    message: str

# Health check
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Main endpoint
@app.post("/run-agent")
async def run_agent(request: AgentRequest):
    try:
        # Pick agent type
        if request.agent_type.lower() == "remediator":
            agent = get_remediator_agent(authorized_namespace)
        elif request.agent_type.lower() == "chat":
            agent = get_chat_agent(authorized_namespace)
        else:
            raise HTTPException(status_code=400, detail="Invalid agent_type")

        # Prepare session data
        session_data = {
            "user_id": request.user_id,
            "session_id": request.session_id
        }

        # Run agent asynchronously
        logger.info(f"Agent type: {request.agent_type}, Namespace: {authorized_namespace}")
        logger.info(f"Session data: {session_data}")
        logger.info(f"Message: {request.message[:200]}")  # first 200 chars
        logger.info(f"Agent instance: {agent}")
        response = await run(agent, session_data, request.message)
        return {"response": response}

    except Exception as e:
        logger.error(f"Agent call failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
