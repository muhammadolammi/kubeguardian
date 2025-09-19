from const import get_ENV, logger
from pydantic import BaseModel
import os
import uvicorn
from google.adk.cli.fast_api import get_fast_api_app
import jwt
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta, timezone
from fastapi import Response, Request, FastAPI

from helpers import AlertDB,AuthDBHelper

session_DB_URL = get_ENV("SESSION_DB_URL")
AI_AGENT_URL = get_ENV("AI_AGENT_URL")
DB_URL = get_ENV("DB_URL")
CRYPT_KEY = get_ENV("CRYPT_KEY")
authdb_helper = AuthDBHelper(db_url=DB_URL, crypt_key=CRYPT_KEY)
alertdb = AlertDB(db_url=DB_URL, crypt_key=CRYPT_KEY)

JWT_SECRET = CRYPT_KEY
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_MINUTES = 60  # 1 hour


class SessionRequest(BaseModel):
    user_id: str

class ChatRequest(BaseModel):
    session_id: str
    user_id: str
    message: str

class RegRequest(BaseModel):
    username: str
    email: str
    password: str
class LoginRequest(BaseModel):
    email: str
    password: str

# Get the directory where main.py is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Example session service URI (e.g., SQLite)
SESSION_SERVICE_URI = session_DB_URL
# Example allowed origins for CORS
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
# Set web=True if you intend to serve a web interface, False otherwise
SERVE_WEB_INTERFACE = False

# Call the function to get the FastAPI app instance
# Ensure the agent directory name ('capital_agent') matches your agent folder
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service_uri=SESSION_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)


@app.post("/register")
async def register(req: RegRequest):
    try:
        user_id = authdb_helper.create_user(user_name=req.username, email=req.email,password=req.password)
        logger.info("user created succesfully. user_id{user_id}")
        return f"user created succesfully. user_id{user_id}"
    except Exception as e:
        logger.info(f"error creating user. error:{e}")
        return f"error creating user. error:{e}"
        

@app.post("/login")
async def login(req: LoginRequest, response: Response):
    passState = authdb_helper.verify_password(email=req.email, password=req.password)
    if passState is None:
        return JSONResponse(content={"error": f"No user for given email :{req.email}"}, status_code=401)
    if not passState:
        return JSONResponse(content={"error": f"Wrong password for user email {req.email}"}, status_code=401)

    user = authdb_helper.get_user_by_email(email=req.email)

    payload = {
        "user_id": user["id"],
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXP_DELTA_MINUTES)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
   #TODO set secure to true
    response.set_cookie(
        key="jwt_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False  # must be False on localhost
    )

    return {
        "id": user["id"],
        "user_name": user["user_name"],
        "email": user["email"]
    }
@app.get("/custom-alerts")
async def custom_alerts():
    try:
        dbs = alertdb.get_all_alerts()
        return dbs
    except Exception as e:
        logger.info(f"error encountered: {e}")
        return {f"error encountered: {e} "}


@app.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="jwt_token")
    return {"message": "Logged out successfully"}
@app.delete("/users/{user_id}")
async def delete_user(user_id:str):
    authdb_helper.delete_user(user_id)

@app.get("/me")
async def me(req: Request):
    token = req.cookies.get("jwt_token")
    if not token:
        return JSONResponse(content={"error": "Unauthorized"}, status_code=401)
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        user = authdb_helper.get_user_by_id(user_id)
        if not user:
            return JSONResponse(content={"error": "User not found"}, status_code=401)
        return {"id": user["id"], "user_name": user["user_name"], "email": user["email"]}
    except jwt.ExpiredSignatureError:
        return JSONResponse(content={"error": "Token expired"}, status_code=401)
    except jwt.InvalidTokenError:
        return JSONResponse(content={"error": "Unauthorized"}, status_code=401)

if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, defaulting to 8081
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8081)))