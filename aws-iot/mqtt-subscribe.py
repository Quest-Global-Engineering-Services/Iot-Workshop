# DHTtoAWSIoTPublisher.py 

import time
import board 
import json
import logging 
import datetime
import paho.mqtt.client as mqtt 
from time import sleep

# Initialize logging
logging.basicConfig(level=logging.INFO) 

def load_aws_config():
    return {
        "host": 'abcedfghijk-ats.iot.us-east-1.amazonaws.com',
        "port": 8883,
        "client_id": 'RaspThing',
        "ca_path": './AmazonRootCA1.pem',
        "cert_path": './9adf8ea65911a43e615e37e62bab614b22dfb134b5b94b45e7fcb9068e5da8d5-certificate.pem.crt',
        "key_path": './9adf8ea65911a43e615e37e62bab614b22dfb134b5b94b45e7fcb9068e5da8d5-private.pem.key',         
        "subscriberTopic": "my-subscriber"
    }

 
# MQTT Callback when a message is received
def on_connect(client, userdata, flags, rc):
    logging.info(f"Connected with result code {rc}")
    client.subscribe(AWS_CONFIG["subscriberTopic"])

def on_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode("utf-8"))
        logging.info(payload)
    except Exception as e:
        logging.error(f"Error: {str(e)}")    
    sleep(5)  # Sleep for 5 seconds

# Main loop for reading and publishing sensor data
try:

    global AWS_CONFIG 

    AWS_CONFIG = load_aws_config()
    mqtt_client = mqtt.Client(client_id=AWS_CONFIG["client_id"])
    mqtt_client.tls_set(
        ca_certs=AWS_CONFIG["ca_path"],
        certfile=AWS_CONFIG["cert_path"],
        keyfile=AWS_CONFIG["key_path"]
    )
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(AWS_CONFIG["host"], port=AWS_CONFIG["port"])
    mqtt_client.loop_start()
    while True:
        time.sleep(2)
except KeyboardInterrupt:
    pass
finally:
    mqtt_client.disconnect()
    logging.info('MQTT client disconnected')


