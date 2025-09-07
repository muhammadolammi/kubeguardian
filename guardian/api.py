


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
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
    namespace: str = "default"  # namespace context
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
            agent = get_remediator_agent(request.namespace)
        elif request.agent_type.lower() == "chat":
            agent = get_chat_agent(request.namespace)
        else:
            raise HTTPException(status_code=400, detail="Invalid agent_type")

        # Prepare session data
        session_data = {
            "user_id": request.user_id,
            "session_id": request.session_id
        }

        # Run agent asynchronously
        response = await run(agent, session_data, request.message)
        return {"response": response}

    except Exception as e:
        logger.error(f"Agent call failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
