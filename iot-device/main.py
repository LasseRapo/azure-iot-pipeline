import os
import random
import time
from azure.iot.device import IoTHubDeviceClient

CONNECTION_STRING = os.getenv("IOT_HUB_CONNECTION_STRING")

if not CONNECTION_STRING:
    raise ValueError("IOT_HUB_CONNECTION_STRING environment variable is not set.")

client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

def simulate_temperature():
    # Simulate a temperature measurement
    return round(random.uniform(-10.0, 30.0), 2)

def monitor_temperature():
    while True:
        upper_limit = 28.0  # Upper limit for temperature
        lower_limit = -8.0  # Lower limit for temperature

        temperature = simulate_temperature()

        if temperature > upper_limit or temperature < lower_limit:
            print(f"Temperature out of range: {temperature:.2f}°C")

            client.send_message(f"Temperature out of range: {temperature:.2f}°C")
        else:
            print(f"Temperature is normal: {temperature:.2f}°C")
        
        # Sleep for a while before the next measurement
        time.sleep(5)

if __name__ == "__main__":
    try:
        client.connect()
        print("Connected to IoT Hub")
    except Exception as e:
        print(f"Failed to connect to IoT Hub: {e}")
    monitor_temperature()
