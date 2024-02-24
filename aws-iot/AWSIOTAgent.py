# DHTtoAWSIoTPublisher.py 

import time
import board
import adafruit_dht
import json
import logging 
import datetime
import paho.mqtt.client as mqtt 
from RPLCD.i2c import CharLCD 
from time import sleep

# Initialize logging
logging.basicConfig(level=logging.INFO)

def read_sensor_data(dht_sensor):
    """Read and return sensor data as a tuple (temperature, humidity)."""
    try:
        temperature = dht_sensor.temperature
        humidity = dht_sensor.humidity
        return temperature, humidity
    except RuntimeError as e:
        logging.error(f"Runtime error in read_sensor_data: {e}")
        return None, None


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
        "host": 'abcdefghijk.iot.us-east-1.amazonaws.com',
        "port": 8883,
        "client_id": 'RaspThing',
        "ca_path": './AmazonRootCA1.pem',
        "cert_path": './9adf8ea65911a43e615e37e62bab614b22dfb134b5b94b45e7fcb9068e5da8d5-certificate.pem.crt',
        "key_path": './9adf8ea65911a43e615e37e62bab614b22dfb134b5b94b45e7fcb9068e5da8d5-private.pem.key',
        "publisherTopic": "DHTSENSE",
        "subscriberTopic": "DHTThresholdReceiver"
    }

def load_lcd_config():
    return {
        "i2c_expander": "PCF8574",
        "i2c_address": 0x27,
        "cols": 16,
        "rows": 2
    }

# Initialize LCD display
def initialize_lcd(lcd_config):
    return CharLCD(
        i2c_expander=lcd_config["i2c_expander"],
        address=lcd_config["i2c_address"],
        port=1,
        cols=lcd_config["cols"],
        rows=lcd_config["rows"]
    )

# MQTT Callback when a message is received
def on_connect(client, userdata, flags, rc):
    logging.info(f"Connected with result code {rc}")
    client.subscribe(AWS_CONFIG["subscriberTopic"])

def on_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode("utf-8"))
        parameter = payload.get("Parameter")
        value = payload.get("Value")
        logging.info(f"to LCD: Parameter: {parameter}, Value: {value}")
        if value is not None:
            display_on_lcd(lcd, parameter, value)

    except Exception as e:
        logging.error(f"Error: {str(e)}")
    
    sleep(5)  # Sleep for 5 seconds

# Function to display messages on LCD
def display_on_lcd(lcd, parameter, value):
    lcd.clear()
    if parameter == 'temperature':
        lcd.write_string(f"Temperature: {value}C")
    elif parameter == 'humidity':
        lcd.write_string(f"Humidity: {value}%")
    logging.info(f"Parameter: {value}")
     

# LCD realted code ends

 

DEVICE ='PI1'

# Initialize the DHT sensor
dht_sensor = adafruit_dht.DHT11(board.D4)

 

# Main loop for reading and publishing sensor data
try:

    global AWS_CONFIG, lcd

    AWS_CONFIG = load_aws_config()
    lcd_config = load_lcd_config()

    lcd = initialize_lcd(lcd_config)

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
        temperature, humidity = read_sensor_data(dht_sensor)
        if temperature is not None and humidity is not None:
            timestamp = int(datetime.datetime.now().timestamp())
            logging.info(f"Temperature: {temperature}°C, Humidity: {humidity}%, Timestamp: {timestamp}, Device: {DEVICE}")
            sensor_data = {"temperature": temperature, "humidity": humidity,"timestamp": timestamp, "device": DEVICE}
            payload = json.dumps(sensor_data)             
            publish_to_aws(mqtt_client, AWS_CONFIG["publisherTopic"], payload)
        time.sleep(2)  # Time delay can be made configurable
except KeyboardInterrupt:
    pass
finally:
    mqtt_client.disconnect()
    logging.info('MQTT client disconnected')


