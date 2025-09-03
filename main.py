import asyncio
from stream import stream_pods 
import argparse
from const import logger, agent
from guardian.run import run



import logging

def enable_chat_mode(chat_mode: bool):
    if chat_mode:
        # Disable all logging
        logging.disable(logging.CRITICAL)
    else:
        # Re-enable logging
        logging.disable(logging.NOTSET)

def start_chat_mode(agent):
    enable_chat_mode(True)
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
            
            ai_response = asyncio.run(run(agent, str(payload_config)))
            
            print("\nAgent:")
            print(ai_response)
            print("-" * 50)

        except KeyboardInterrupt:
            print("\nExiting chat mode. Goodbye!")
            break
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chat-mode", action="store_true", help="Enable chat mode", required=True)
    args = parser.parse_args()
    if args.chat_mode:
       start_chat_mode(agent=agent)
    else:
        ioloop = asyncio.get_event_loop()
        ioloop.create_task(stream_pods())
        #TODO create looop for other streams
        # ioloop.create_task(deployments())
        ioloop.run_forever()
if __name__ == "__main__":
    main()
