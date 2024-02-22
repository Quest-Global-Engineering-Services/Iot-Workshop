# DHTtoAWSIoTPublisher.py 

import time
import json
import logging 
import datetime
from RPLCD.i2c import CharLCD 
from time import sleep

# Initialize logging
logging.basicConfig(level=logging.INFO)
 
# Load LCD configuration
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

# Function to display messages on LCD
def display_on_lcd(lcd):
    logging.info('Have a great start')    
    lcd.clear()
    lcd.write_string("Have a great start") 
    time.sleep(2) 

# Main loop for reading and publishing sensor data
try:

    global lcd     
    lcd_config = load_lcd_config()
    lcd = initialize_lcd(lcd_config)
    while True:
         display_on_lcd(lcd)
except KeyboardInterrupt:
    pass
finally:    
    logging.info('client disconnected')


