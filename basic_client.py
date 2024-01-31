import requests

# URL of the Flask server's analyze endpoint
url = 'http://localhost:5000/analyze'

# Simulate the value that triggers the transition in the FSM
# This should be a number that satisfies one of the conditions.
# For example, to satisfy "x>3", you might use 4.
value_to_trigger_transition = 33

# NGSI-LD formatted data
data = {'id': 'urn:ngsi-ld:Notification:ad816090-bc38-11ee-b577-0242ac12000a', 'type': 'Notification', 'subscriptionId': 'urn:ngsi-ld:Subscription:fd03603e-bc36-11ee-b577-0242ac12000a', 'notifiedAt': '2024-01-26T10:50:11.012Z', 'data': [{'id': 'urn:ngsi-ld:TemperatureSensor:001', 'type': 'TemperatureSensor', 'temperature': value_to_trigger_transition}]}

# Headers to indicate that we're sending JSON-LD formatted as NGSI-LD
headers = {
    'Content-Type': 'application/ld+json'
}

# Send the POST request
response = requests.post(url, json=data, headers=headers)

# Print out the response from the server
print(response.text)
