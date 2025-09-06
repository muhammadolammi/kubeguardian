


import pika
import sys
import json
import os
from session.session import create_new_session
from guardian.agent import get_remediator_agent
from google.adk import Agent
import asyncio
from guardian.run import run

EVENTS=["ERROR", "DELETED", "WARNING", "ADDED"]
def make_callback(agent: Agent, session_data:dict):
    def callback(ch, method, properties, body):
            message = json.loads(body.decode("utf-8"))
            event_type = message.get("type")
            deployment = message.get("deployment_name")
            reason = message.get("reason")
            #This is where we call our remediator.
            # For now just one session is enough for remediator, so it have all context from the start of the program


            print(f"[x] Received event: {event_type} for {deployment} (Reason: {reason})")
            # We can move this logic to or prompt level , and tell AI what to do base on event 
            # We are calling ai in non async func so we use asyncio.run
            asyncio.run(run(agent=agent, session_data=session_data, message=body))

            # # Now act based on the event type
            # if event_type == "ADDED":
            #     pass
            #     handle_added(deployment, reason)
            # elif event_type == "DELETED":
            #     handle_deleted(deployment, reason)
            # elif event_type == "ERROR":
            #     handle_error(deployment, reason)
            # else:
            #     handle_other(event_type, deployment, reason)
    return callback
def deployment_sub(agent: Agent, namespace:str, session_data:dict):

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    # declare all routings you wants to subscribe to 
    # rn just all our events
    # redeclare exchange , (we dont care pub declare it to avoid error)
    channel.exchange_declare(exchange=f"{namespace}_deployments", exchange_type='direct', durable=True)
    #Create a queue base on routing, this queue stay active , so if our consumer go offline, message stay on queue
    channel.queue_declare(queue=f"{namespace}_deployment_queue", durable=True)

    for event in EVENTS:
        # Bind queue to exchange and route base on event 
        channel.queue_bind(
        exchange=f"{namespace}_deployments", queue=f"{namespace}_deployment_queue", routing_key=event)
    #consume
    callback = make_callback(agent, session_data)
    channel.basic_consume(
    queue=f"{namespace}_deployment_queue", on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

def main():
    # Create the remediator session here , onces 
    # WE can alwasy move this logic , maybe get it from env
    authorized_namespace = "bank-of-anthos"
    agent = get_remediator_agent(authorized_namespace)
    session_id = create_new_session("remediator")
    deployment_sub(agent, authorized_namespace, {"user_id":"remediator", "session_id":session_id})

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)