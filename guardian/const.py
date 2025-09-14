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