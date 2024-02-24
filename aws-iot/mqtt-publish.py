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

 

def publish_to_aws(mqtt_client, topic, message):
    """Publish a message to an AWS IoT MQTT topic."""
    try:
        result = mqtt_client.publish(topic, message)
        status = result[0]
        if status == 0:
            logging.info(f"Data published to AWS IoT topic {topic}")
        else:
            logging.info(f"Failed: Data publish to AWS IoT topic")
        
    except Exception as e:
        logging.error(f"Publish error: {e}")

# LCD related code starts
# Load LCD configuration

def load_aws_config():
    return {
        "host": 'abcedfghijk-ats.iot.us-east-1.amazonaws.com',
        "port": 8883,
        "client_id": 'RaspThing',
        "ca_path": './AmazonRootCA1.pem',
        "cert_path": './9adf8ea65911a43e615e37e62bab614b22dfb134b5b94b45e7fcb9068e5da8d5-certificate.pem.crt',
        "key_path": './9adf8ea65911a43e615e37e62bab614b22dfb134b5b94b45e7fcb9068e5da8d5-private.pem.key',
        "publisherTopic": 'my-publisher'         
    }

 
 

 

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
    mqtt_client.connect(AWS_CONFIG["host"], port=AWS_CONFIG["port"])
    mqtt_client.loop_start()
    while True:
        payload = json.dumps({"Message": "Hello from Pi"})
        publish_to_aws(mqtt_client, AWS_CONFIG["publisherTopic"], payload)            
        time.sleep(2)  # Time delay can be made configurable
except KeyboardInterrupt:
    pass
finally:
    mqtt_client.disconnect()
    logging.info('MQTT client disconnected')


