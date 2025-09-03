import os
import logging
import sys
from guardian.agent import get_orchestrator_agent



# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,  # ✅ Logs to stderr
)
logger = logging.getLogger(__name__)


#ONE agent for all session
agent = get_orchestrator_agent()
