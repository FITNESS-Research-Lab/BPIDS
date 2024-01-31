from flask import Flask, request, jsonify
import json
import operator
from confluent_kafka import Consumer
from confluent_kafka import Producer
import os
import socket
from dotenv import load_dotenv
import requests
load_dotenv()
consumer_topic = "basetopic"

CONSUMER_CONFIG = {
    "client.id": os.getenv("KAFKA_CLIENT_ID", "python-kafka-client"),
    "group.id": os.getenv("KAFKA_CONSUMER_GROUP_ID", "python-kafka-consumer"),
    "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka.broker.eu:9092"),
    "auto.offset.reset": "earliest",
    "security.protocol": "SSL",
    "ssl.ca.location": os.getenv("SSL_CA_LOCATION", "ssl/ca-cert.pem"),
    "ssl.certificate.location": os.getenv("SSL_CERTIFICATE_LOCATION", "ssl/service-cert.pem"),
    "ssl.key.location": os.getenv("SSL_KEY_LOCATION", "ssl/service-key.pem")
}


with open(os.getenv("SSL_PASSWORD_LOCATION", "ssl/service.pwd"), "r") as file:
    CONSUMER_CONFIG["ssl.key.password"] = file.read().strip()




hostname = socket.gethostname()
consumer = Consumer(CONSUMER_CONFIG)

consumer.subscribe([consumer_topic])


while True:
    try:
        # SIGINT can't be handled when polling, limit timeout to 1 second.
        record = consumer.poll(1.0)
        if record is None:
            continue

        if record is not None:
            try:
                # Parse the message value as JSON
                json_data = json.loads(record.value().decode('utf-8'))
                print('Received JSON message:')
                print(json.dumps(json_data, indent=2))  # Pretty-print the JSON data
                response = requests.post("http://localhost:5000/analyze", json=json_data)
                if response.status_code == 200:
                    print('Message forwarded successfully')
                else:
                    print(f'Error forwarding message: {response.status_code}')
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
    except KeyboardInterrupt:
        # Handle keyboard interrupt (e.g., Ctrl+C) to gracefully exit the loop.
        break

    #consumer.close()



#TO READ ONLY THE LAST MESSAGE PRESENT IN THE TOPIC
"""
while True:
    try:
        # SIGINT can't be handled when polling, limit timeout to 1 second.
        record = None
        while record is None:
            record = consumer.poll(1.0)
            if record is None:
                partitions = consumer.assignment()
                for partition in partitions:
                    # Seek to the end of each partition
                    consumer.seek(partition, consumer.get_watermark_offsets(partition)[1])

        # Parse the message value as JSON
        try:
            json_data = json.loads(record.value().decode('utf-8'))
            print('Received JSON message:')
            print(json.dumps(json_data, indent=2))  # Pretty-print the JSON data
            response = requests.post("http://localhost:5000/analyze", json=json_data)
            if response.status_code == 200:
                print('Message forwarded successfully')
            else:
                print(f'Error forwarding message: {response.status_code}')
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")

        # Exit the loop after processing the last message
        break

    except KeyboardInterrupt:
        # Handle keyboard interrupt (e.g., Ctrl+C) to gracefully exit the loop.
        break

consumer.close()

"""
