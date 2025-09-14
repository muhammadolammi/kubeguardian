from const import get_ENV
session_DB_URL = get_ENV("SESSION_DB_URL")
import os
import uvicorn
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
# Get the directory where main.py is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"This is agent dir {AGENT_DIR} yeah")
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



if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, defaulting to 8081
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8081)))