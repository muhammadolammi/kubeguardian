import asyncio
from stream import stream_pods 
import argparse
from const import  chat_agent
from guardian.run import run



import logging

def set_chat_mode(chat_mode: bool):
     # Disable or enable logging based on chat_mode
    logging.disable(logging.CRITICAL if chat_mode else logging.NOTSET)

    # Write to file
    with open("chat.env", "w") as f:
        f.write(f"CHAT_MODE={'True' if chat_mode else 'False'}\n")

def start_chat_mode(agent):
    
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
            
            ai_response = asyncio.run(run(agent, f"{payload_config}", "chat_response"))
            
            print("\nAgent:")
            print(ai_response or "⚠️ No response generated")
            print("-" * 50)

        except KeyboardInterrupt:
            print("\nExiting chat mode. Goodbye!")
            break
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chat-mode", action="store_true", help="Enable chat mode")
    args = parser.parse_args()
    if args.chat_mode:
       set_chat_mode(True)
       start_chat_mode(agent=chat_agent)
    else:
        set_chat_mode(False)
        ioloop = asyncio.get_event_loop()
        ioloop.create_task(stream_pods())
        #TODO create looop for other streams
        # ioloop.create_task(deployments())
        ioloop.run_forever()
if __name__ == "__main__":
    main()
