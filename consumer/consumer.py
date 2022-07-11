#!/usr/bin/env python
import pika
import os
from time import sleep
import json

def pdf_process_function(msg):
    print(" PDF processing")
    print(" [x] Received " + str(msg))
    sleep(5) # delay for 5 seconds
    print(" PDF processing finished")
    return

# Access the CLOUD_AMQP_URL environment variable and parse it (fallback to localhost)
url = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@127.0.0.2:5672/%2f')
print(url)
params = pika.URLParameters(url)
params.socket_timeout = 10
connection = pika.BlockingConnection(params)

channel = connection.channel()

channel.queue_declare(queue='rpc_queue')

def message_to_send():
    message = dict(service='service-received', body="Sou o listening")
    return json.dumps(message)

def on_request(ch, method, props, body):
    message_received = json.loads(body)
    print(f" [.] {message_received}")

    response = message_to_send()
    print(f"response: {response}")

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

print(" [x] Awaiting RPC requests")
channel.start_consuming()
