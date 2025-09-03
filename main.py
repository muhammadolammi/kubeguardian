import asyncio
from stream import stream_pods




def main():
    ioloop = asyncio.get_event_loop()
    ioloop.create_task(stream_pods())
    #TODO create looop for other streams
    # ioloop.create_task(deployments())
    ioloop.run_forever()
if __name__ == "__main__":
    main()
