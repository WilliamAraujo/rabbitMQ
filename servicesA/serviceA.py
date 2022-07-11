#!/usr/bin/env python
import pika
import os
from time import sleep
import uuid
import json


class RabbitMQRpcClient(object):

    def __init__(self):
        # Access the CLOUD_AMQP_URL environment variable and parse it (fallback to localhost)
        url = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@172.17.0.1:5672/%2f')
        print(url)
        params = pika.URLParameters(url)
        params.socket_timeout = 12
        self.connection = pika.BlockingConnection(params)
        print("[serviceA] RabbitMQ Connected !")

        print(self.connection)      

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=str(n))
        self.connection.process_data_events(time_limit=None)
        return self.response


client_rpc = RabbitMQRpcClient()

count = 1
while(True):
    message = dict(service='serviceA', body=f"Sou o serviceA", count=count)
    print(f" [x] {message}")
    response = client_rpc.call(json.dumps(message))
    print(f" [.] Got {json.loads(response)}")
    count+=1
    sleep(1)
