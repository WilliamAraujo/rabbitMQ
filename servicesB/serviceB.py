#!/usr/bin/env python
import pika
import uuid
import json


class RabbitMQRpcClient(object):

    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='eth0'))

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

message = dict(service='serviceB', body="Sou o serviceB")

print(f" [x] {message}")
response = client_rpc.call(json.dumps(message))
print(f" [.] Got {json.loads(response)}")