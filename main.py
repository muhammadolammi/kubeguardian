import asyncio
from stream import stream_pods , stream_deployments
import argparse
from const import  chat_agent
from guardian.run import run
from sessions.sessions import create_new_session 
from google.adk.sessions import InMemorySessionService




import logging

def set_chat_mode(chat_mode: bool):
     # Disable or enable logging based on chat_mode
    logging.disable(logging.CRITICAL if chat_mode else logging.NOTSET)

    # Write to file
    with open("chat.env", "w") as f:
        f.write(f"CHAT_MODE={'True' if chat_mode else 'False'}\n")

def start_chat_mode(agent,session_service,session_data, namespace):
    
    print("Welcome to KubeGuardian Chat Mode! 🎯")
    print("You can take action on your Kubernetes cluster right here in the terminal.")
    print("Type 'quit' to exit.\n")

    payload_config = {"user_type": "admin", "authorize_namespace": namespace}  # Could extend to dev, viewer, etc.

    while True:
        try:
            user_input = input("User: ").strip()  # Clean input
            if not user_input:
                continue  # Ignore empty input
            
            if user_input.lower() == "quit":
                print("Goodbye!")
                break

            payload_config["user_message"] = user_input
            
            ai_response = asyncio.run(run(agent,session_service, session_data, f"{payload_config}", "chat_response"))
            
            print("\nAgent:")
            print(ai_response or "⚠️ No response generated")
            print("-" * 50)

        except KeyboardInterrupt:
            print("\nExiting chat mode. Goodbye!")
            break
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chat-mode", action="store_true", help="Enable chat mode")
    parser.add_argument("--namespace",  help="An authorized namespace is required", required=True, type=str)
    args = parser.parse_args()
    namespace = args.namespace
    #TODO determin when to actually create new session when we introduce web ui for the chat
    # For now this suffice cause every run will create a new session
    # We can decide to add sessions management later
    session_service = InMemorySessionService()
    #TODO add a db that actually store users and get current user for the web ui
    user_id = "test"
    session_id = asyncio.run(create_new_session(session_service, user_id))
    session_data = {"user_id":user_id, "session_id":session_id}
    if args.chat_mode:
       set_chat_mode(True)
       start_chat_mode(agent=chat_agent,session_service=session_service,session_data=session_data, namespace=namespace)

    else:
        set_chat_mode(False)
        ioloop = asyncio.get_event_loop()
        ioloop.create_task(stream_pods(namespace , session_service, session_data))
        ioloop.create_task(stream_deployments(namespace, session_service, session_data))
        #TODO create looop for other streams
        # ioloop.create_task(deployments())
        ioloop.run_forever()
if __name__ == "__main__":
    main()
