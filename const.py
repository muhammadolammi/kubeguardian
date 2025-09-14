import os
from dotenv import load_dotenv


def get_ENV(name :str) -> str:
    # load variables from .env file
    load_dotenv()
    env = os.getenv(name) 

    if not env:
        print(f"{name} not in environment")
        os._exit(1)
    return env
APP_NAME = "kubeguardian"



import logging
import sys



# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,  # ✅ Logs to stderr
)
logger = logging.getLogger(__name__)





