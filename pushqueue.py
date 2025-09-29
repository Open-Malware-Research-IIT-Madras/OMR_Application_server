"""
Module Name: pushqueue.py

Description:
    Simple RabbitMQ publisher script. Establishes a connection to a
    RabbitMQ server using credentials, declares a queue, and publishes
    a test message. Includes an alternate implementation with exception
    handling for connection errors.

Functions:
    None defined explicitly in this file.

Classes:
    None defined explicitly in this file.

Usage:
    Run this script directly to send a test message to the queue:
        python rabbitmq_publisher.py

Author:
    Allan Pais
"""

import pika 

credentials = pika.PlainCredentials('OMR_RMQ', 'Omr@123')
connection = pika.BlockingConnection(pika.ConnectionParameters('172.23.254.74', 5672, '/', credentials))

channel =connection.channel()

channel.queue_declare("queue_1")

channel.basic_publish(exchange='',
                      routing_key='queue_1',
                      body="Test")

print(" [x] Sent 'Text Message!'")

"""
import pika
import sys

try:
    credentials = pika.PlainCredentials('OMR_RMQ', 'Omr@123')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='172.23.254.74',
            port=5672,
            virtual_host='/',
            credentials=credentials
        )
    )
    channel = connection.channel()

    channel.queue_declare(queue='queue_1')

    channel.basic_publish(
        exchange='',
        routing_key='queue_1',
        body='Test'
    )

    print(" [x] Sent 'Test Message!'")

except pika.exceptions.AMQPConnectionError as e:
    print(f"Failed to connect to RabbitMQ: {e}")
    sys.exit(1)
finally:
    if connection and connection.is_open:
        connection.close()
"""

