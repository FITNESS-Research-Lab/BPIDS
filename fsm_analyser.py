from flask import Flask, request, jsonify
import json
import operator
from confluent_kafka import Consumer, Producer
import os
import socket
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from a .env file
load_dotenv()

# Kafka Producer Configuration
producer_topic = "BP_IDS_Analysis"
PRODUCER_CONFIG = {
    "client.id": os.getenv("KAFKA_CLIENT_ID", "python-kafka-client"),
    "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka.broker.eu:9092"),
    "security.protocol": "SSL",
    "ssl.ca.location": os.getenv("SSL_CA_LOCATION", "ssl/ca-cert.pem"),
    "ssl.certificate.location": os.getenv("SSL_CERTIFICATE_LOCATION", "ssl/service-cert.pem"),
    "ssl.key.location": os.getenv("SSL_KEY_LOCATION", "ssl/service-key.pem")
}

# FSM Configuration
with open('prosumer_fsm_structure.json', 'r') as fsm_file:
    fsm = json.load(fsm_file)

# Comparison Operators
ops = {
    '>': operator.gt,
    '<': operator.lt,
    '>=': operator.ge,
    '<=': operator.le,
    '==': operator.eq,
    '!=': operator.ne
}

# Initialize the current state
current_state = fsm['initial_state']


# Function to evaluate conditions
def evaluate_condition(condition, value):
    for op_symbol, op_function in ops.items():
        if op_symbol in condition:
            _, threshold = condition.split(op_symbol)
            threshold = threshold.strip()
            try:
                threshold_value = float(threshold)
                if op_symbol in ('>', '<', '==', '!=', '>=', '<='):
                    return op_function(value, threshold_value)
            except ValueError:
                return False
    return False


# Function to send data to Kafka
def send_to_kafka(data):
    print("Sending Update to Kafka")
    #print(data)
    with open(os.getenv("SSL_PASSWORD_LOCATION", "ssl/service.pwd"), "r") as file:
        PRODUCER_CONFIG["ssl.key.password"] = file.read().strip()

    producer = Producer(PRODUCER_CONFIG)
    value_bytes = json.dumps(data).encode('utf-8')
    producer.produce(topic=producer_topic, value=value_bytes)
    producer.flush()


@app.route('/analyze', methods=['POST'])
def analyze():
    global current_state

    data = request.json
    entity_data = data.get('data', [{}])[0]  # Assuming the first entity contains the relevant data

    for transition in fsm['transitions']:
        if current_state == transition['source']:
            condition = transition['condition']

            # Find the comparison operator in the condition
            operator_found = None
            for op_symbol in ['>', '<', '>=', '<=', '==', '!=']:
                if op_symbol in condition:
                    operator_found = op_symbol
                    break

            if operator_found:
                keyword, threshold = condition.split(operator_found, 1)
                keyword = keyword.strip()
                threshold = threshold.strip()
                value = entity_data.get(keyword)

                if value is not None:
                    try:
                        incoming_value = float(value)
                    except (ValueError, TypeError):
                        return jsonify({'result': 'Invalid value'}), 400

                    if evaluate_condition(condition, incoming_value):
                        current_state = transition['target']
                        result = {'result': 'Transition successful', 'new_state': current_state}
                        send_to_kafka(result)
                        return jsonify({
                            'result': 'Transition successful',
                            'new_state': current_state
                        })

    return jsonify({'result': 'No transition met', 'current_state': current_state}), 404


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
