import os
import logging
import sys
from guardian.agent import get_orchestrator_agent, get_chat_agent



# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,  # ✅ Logs to stderr
)
logger = logging.getLogger(__name__)


#agents for all session
orchestrator_agent = get_orchestrator_agent()
chat_agent = get_chat_agent()

APP_NAME = "kubeguardian"
