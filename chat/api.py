from const import get_agent_ai_url
AI_AGENT_URL = get_agent_ai_url()


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from guardian.run import run
from session.session import create_new_session, get_session, delete_session
import httpx  

app = FastAPI()
#Lets use sqlite to test

class SessionRequest(BaseModel):
    user_id: str

class ChatRequest(BaseModel):
    session_id: str
    user_id: str
    message: str
    namespace: str

@app.post("/session")
async def create_session(req: SessionRequest):
    session_id = await create_new_session( req.user_id)
    return {"session_id": session_id}

@app.get("/session/{session_id}")
async def read_session(session_id: str):
    session = get_session( session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "user_id": session.user_id}

@app.delete("/session/{session_id}")
async def remove_session(session_id: str):
    await delete_session( session_id)
    return {"message": "Session deleted"}
 
@app.post("/chat")
async def chat(req: ChatRequest):
    # Call agent service
    payload = {
        "agent_type": "chat",
        "namespace": req.namespace,
        "user_id": req.user_id,
        "session_id": req.session_id,
        "message": req.message
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(AI_AGENT_URL, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            return {"response": data.get("response")}
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"AI agent call failed: {str(e)}")
