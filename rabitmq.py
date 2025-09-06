import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

channel = connection.channel()

channel.exchange_delete(exchange="main_deployments")