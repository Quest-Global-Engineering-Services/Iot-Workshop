import adafruit_dht
import board
import time


 
dht_sensor = adafruit_dht.DHT11(board.D4)

while True:
        temperature = dht_sensor.temperature
        humidity = dht_sensor.humidity
        if humidity is not None and temperature is not None:
            print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
        else:
            print('Failed to get reading. Try again!');
        time.sleep(3);