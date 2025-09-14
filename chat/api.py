from const import get_ENV
AI_AGENT_URL = get_ENV("AI_AGENT_URL")


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx  
import uuid

app = FastAPI()

class SessionRequest(BaseModel):
    user_id: str

class ChatRequest(BaseModel):
    session_id: str
    user_id: str
    message: str

@app.post("/session")
async def create_session(req: SessionRequest):
    async with httpx.AsyncClient() as client:
        try:
            session_id = f"session_{uuid.uuid4().hex[:7]}"
            resp = await client.post(f"{AI_AGENT_URL}/apps/chat/users/{req.user_id}/sessions/{session_id}", timeout=60)
            resp.raise_for_status()
            return {"session_id": session_id}
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"AI agent call failed: {str(e)}")

@app.get("/{user_id}/sessions/{session_id}")
async def read_session(user_id:str, session_id: str):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{AI_AGENT_URL}/apps/chat/users/{user_id}/sessions/{session_id}", timeout=60)
            resp.raise_for_status()
            data = resp.json()
            return {"response": data}
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"AI agent call failed: {str(e)}")

@app.delete("/{user_id}/sessions/{session_id}")
async def remove_session(user_id:str,session_id: str):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.delete(f"{AI_AGENT_URL}/apps/chat/users/{user_id}/sessions/{session_id}", timeout=60)
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"AI agent call failed: {str(e)}")

 
@app.post("/chat")
async def chat(req: ChatRequest):
    # Call agent service
    
    payload = {
        "appName": "chat",
        "userId": req.user_id,
        "sessionId": req.session_id,
        "newMessage": {
            "parts": [{
                "text": req.message
                }
                ],
            "role":"user",
            },
        "streaming": False,
        "stateDelta": {}
    }


    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{AI_AGENT_URL}/run", json=payload, timeout=60)
            # print("AI agent response text:", resp.text) 

            resp.raise_for_status()
            data = resp.json()
            # print(data[0]["content"]["parts"][0]["text"])
            final_response_text = data[0]["content"]["parts"][0]["text"]


            return {"response": final_response_text}
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"AI agent call failed: {str(e)}")
