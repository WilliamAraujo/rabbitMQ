#!/usr/bin/env python
import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq.com'))

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
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

print(" [x] Awaiting RPC requests")
channel.start_consuming()
