# orchestrator/service.py
import asyncio
from guardian.run import run
from guardian.agent import get_remediator_agent
from stream import stream_pods, stream_deployments
from sessions.sessions import create_new_session
from google.adk.sessions import DatabaseSessionService

async def main(namespace: str, fs: str):
    session_service = DatabaseSessionService()
    user_id = "orchestrator"
    session_id = await create_new_session(session_service, user_id)
    session_data = {"user_id": user_id, "session_id": session_id}

    remediator_agent = get_remediator_agent(namespace, fs)
    await asyncio.gather(
        stream_pods(remediator_agent, namespace, session_service, session_data),
        stream_deployments(remediator_agent, namespace, session_service, session_data)
    )

if __name__ == "__main__":
    asyncio.run(main("bank-of-anthos", "ss"))
