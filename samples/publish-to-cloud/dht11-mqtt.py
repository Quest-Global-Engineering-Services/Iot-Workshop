import time
import board
import adafruit_dht
import json
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

 

# Define the DHT sensor
dht_sensor = adafruit_dht.DHT11(board.D4)  # Use the appropriate GPIO pin 

# AWS IoT connection parameters

host = 'a3h9q5a7ne3mnp-ats.iot.us-east-1.amazonaws.com'
root_ca_path = '/home/bks-rpi/Downloads/AmazonRootCA1.pem'
cert_path = '/home/bks-rpi/Downloads/9adf8ea65911a43e615e37e62bab614b22dfb134b5b94b45e7fcb9068e5da8d5-certificate.pem.crt'
private_key_path = '/home/bks-rpi/Downloads/9adf8ea65911a43e615e37e62bab614b22dfb134b5b94b45e7fcb9068e5da8d5-private.pem.key'
client_id = 'RaspThing'
'''
host = 'a1jiwzh2mgjqh0-ats.iot.us-east-1.amazonaws.com'
root_ca_path = '/home/pi/myprograms/thing-certs/AmazonRootCA1.pem'
cert_path = '/home/pi/myprograms/thing-certs/certificate.pem.crt'
private_key_path = '/home/pi/myprograms/thing-certs/private.pem.key'
client_id = 'mypi'
'''

 

# Initialize the MQTT client

mqtt_client = AWSIoTMQTTClient(client_id)
mqtt_client.configureEndpoint(host, 8883)
mqtt_client.configureCredentials(root_ca_path, private_key_path, cert_path)

 

# Configure the MQTT connection

mqtt_client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
mqtt_client.configureDrainingFrequency(2)  # Draining: 2 Hz
mqtt_client.configureConnectDisconnectTimeout(10)  # 10 sec
mqtt_client.configureMQTTOperationTimeout(5)  # 5 sec 

# Connect to AWS IoT
mqtt_client.connect()

 

try:
   while True:
       try:
           temperature_c = dht_sensor.temperature
           humidity = dht_sensor.humidity
           print(f"Temperature: {temperature_c}°C")
           print(f"Humidity: {humidity}%")           

           sensor_data = {
               "temperature": temperature_c,
               "humidity": humidity
           }
           payload = json.dumps(sensor_data)
           mqtt_client.publish('DHTSENSE', str(payload), 1)  # Replace with your MQTT topic
           print('Data published to AWS IoT') 

       except RuntimeError as e:
           print(f"Error: {e}. Retrying...")
           continue
       time.sleep(2)  # Wait for 2 seconds before reading and publishing again

except KeyboardInterrupt:
   pass
finally:
   mqtt_client.disconnect()