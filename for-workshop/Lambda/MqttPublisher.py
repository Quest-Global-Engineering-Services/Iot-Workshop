# MqttPublisher.py 

import os
import json
import boto3
import datetime
import dateutil.parser

# Initialize boto3 clients outside of the handler to improve performance
timestream = boto3.client('timestream-query', region_name='us-east-1')
iot = boto3.client('iot-data', region_name='us-east-1')


def lambda_handler(event, context):
    try:
        # More specific Timestream query to fetch only required fields
        # and data from the last one minute
        thresholdTemperature = int(os.environ['THRESHOLD_TEMPERATURE'])         
        thresholdHumidity = int(os.environ['THRESHOLD_HUMIDITY'])        
        query = f"SELECT device, measure_name,measure_value::bigint,time FROM sensordb.DHTVariables WHERE ((measure_name = 'temperature'  AND  measure_value::bigint >= {thresholdTemperature}) OR (measure_name = 'humidity'  AND  measure_value::bigint >= {thresholdHumidity}))   AND time >= ago(1m)"
        print(query)
        query_result = timestream.query(QueryString=query)  
        print(query_result)
        # Use UTC time for more accurate server-side time calculation
        current_time_unix = int(datetime.datetime.utcnow().timestamp())

        # Local set variable to store unique timestamps
        unique_timestamps = set()

        # Initialize temperature and humidity variables         
        device_name = None
        # Iterate through the query results
        for row in query_result['Rows']:
            # Extract relevant data from each row
            device_name =  row['Data'][0]['ScalarValue']            
            measure_name = row['Data'][1]['ScalarValue']
            measure_value = int(row['Data'][2]['ScalarValue'])  
            time_stamp_str = row['Data'][3]['ScalarValue']         

            # Convert the timestamp string to a Unix timestamp
            time_stamp_unix = int(dateutil.parser.parse(time_stamp_str).timestamp())

            
        

            # If both temperature and humidity are available, publish to AWS IoT
            if measure_value is not None:
                # Create a JSON message payload
                message = json.dumps({'Device':device_name,'Timestamp': time_stamp_unix, 'Parameter': measure_name, 'Value': measure_value})
                
                # Define the MQTT topic
                topic = 'DHTThresholdReceiver'

                # Publish the message to AWS IoT
                iot.publish(
                    topic=topic,
                    payload=message
                )

                # Add the timestamp to the set of unique timestamps
                unique_timestamps.add(time_stamp_unix)

        return {
            'statusCode': 200,
            'body': 'Data sent to AWS IoT successfully'
        }

    # Catch specific boto3 errors
    except boto3.exceptions.Boto3Error as e:
        print(f'Boto3 error: {str(e)}')

    # General exception handling for unexpected errors
    except Exception as e:
        print(f'Unexpected error: {str(e)}')
        
    return {
        'statusCode': 500,
        'body': 'Error sending data to AWS IoT.'
    }

