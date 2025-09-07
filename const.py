import os
import logging
import sys



# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,  # ✅ Logs to stderr
)
logger = logging.getLogger(__name__)




APP_NAME = "kubeguardian"
def get_db_url()-> str:
    db_url = os.getenv("DB_URL") 
    if not db_url:
        print("DB URL not in environment")
        os._exit(1)
def get_agent_ai_url()-> str:
    db_url = os.getenv("DB_URL") 
    if not db_url:
        print("Agent-Ai URL not in environment")
        os._exit(1)