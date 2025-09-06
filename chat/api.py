from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from guardian.run import run
from guardian.agent import get_chat_agent
from session.session import create_new_session, get_session, delete_session

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
    session_data = {"user_id": req.user_id, "session_id": req.session_id}
    chat_agent = get_chat_agent(req.namespace)
    response = await run(chat_agent, session_data, req.message, "chat_response")
    return {"response": response}
