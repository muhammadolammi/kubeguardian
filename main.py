import asyncio
from stream import stream_pods , stream_deployments
import argparse
from const import   logger
from guardian.run import run
from session.session import create_new_session 
from google.adk.sessions import InMemorySessionService
from guardian.agent import get_chat_agent, get_remediator_agent



import logging

def set_chat_mode(chat_mode: bool):
     # Disable or enable logging based on chat_mode
    logging.disable(logging.CRITICAL if chat_mode else logging.NOTSET)

    # Write to file
    with open("chat.env", "w") as f:
        f.write(f"CHAT_MODE={'True' if chat_mode else 'False'}\n")

async def start_chat_mode(agent,session_data):
    
    print("Welcome to KubeGuardian Chat Mode! 🎯")
    print("You can take action on your Kubernetes cluster right here in the terminal.")
    print("Type 'quit' to exit.\n")

    payload_config = {"user_type": "admin"}  # Could extend to dev, viewer, etc.

    while True:
        try:
            user_input = input("User: ").strip()  # Clean input
            if not user_input:
                continue  # Ignore empty input
            
            if user_input.lower() == "quit":
                print("Goodbye!")
                break

            payload_config["user_message"] = user_input
            
            ai_response = await (run(agent, session_data, f"{payload_config}"))
            
            print("\nAgent:")
            print(ai_response or "⚠️ No response generated")
            print("-" * 50)

        except KeyboardInterrupt:
            print("\nExiting chat mode. Goodbye!")
            break

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chat-mode", action="store_true", help="Enable chat mode")
    parser.add_argument("--namespace", required=True, type=str,help="Include authorized cluster namespace ")
    args = parser.parse_args()
    namespace = args.namespace

    user_id = "test"
    session_id = await create_new_session(user_id)
    session_data = {"user_id": user_id, "session_id": session_id}

    # if args.chat_mode:
    #     chat_agent = get_chat_agent(namespace)
    #     set_chat_mode(True)
    #     await start_chat_mode(chat_agent, session_data)
    # else:
        # set_chat_mode(False)
        # # First-run no_event orchestration
        # payload = {"message": "deploy bank of anthos"}
        # remediator_agent = get_remediator_agent(namespace)
        # ai_response = await run(remediator_agent, session_data, f"{payload}", "orchestrator_response")
        # logger.info("First-run orchestration result: %s", ai_response)

        # # Start streams concurrently
        # pod_task = asyncio.create_task(stream_pods(remediator_agent, namespace, session_data))
        # deploy_task = asyncio.create_task(stream_deployments(remediator_agent, namespace, session_data))
        # logger.info("Orchestrator started. Streaming pods & deployments...")

        # await asyncio.gather(pod_task, deploy_task)  # runs until cancelled
        #pass
        # We created a new pub sub type of stream so e default ths run to chat
    chat_agent = get_chat_agent(namespace)
    set_chat_mode(True)
    await start_chat_mode(chat_agent, session_data)

if __name__ == "__main__":
    asyncio.run(main())
        
