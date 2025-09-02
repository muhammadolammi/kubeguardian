from guardian.run import run 
from guardian.agent import get_orchestrator_agent
from  stream_k8s_events import stream_k8s_events
import logging
import  asyncio
import sys


# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,  # ✅ Logs to stderr
)
logger = logging.getLogger(__name__)
def handle_event(event):
    agent = get_orchestrator_agent()
    #TODO provide payload here
    response = asyncio.run(run(agent, f"{event}")  )
    logger.info("Autonomous System Started")
    print(response)

def main():
    stream_k8s_events(handle_event)

if __name__ == "__main__":
    main()
