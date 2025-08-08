import os
from dotenv import load_dotenv
from azure.eventhub import EventHubConsumerClient

load_dotenv()

# Connection string and event hub name from environment variables

EVENTHUB_CONNECTION_STRING = os.getenv("EVENTHUB_CONNECTION_STRING")
EVENTHUB_NAME = os.getenv("EVENTHUB_NAME")

if not EVENTHUB_CONNECTION_STRING or not EVENTHUB_NAME:
    raise ValueError("EVENTHUB_CONNECTION_STRING and EVENTHUB_NAME environment variables must be set.")

# Function to process incoming messages
def process_message(partition_context, message):
    print(f"Received message: {message.body_as_str()}")
    partition_context.update_checkpoint(message)

# Create an Event Hub consumer client
client = EventHubConsumerClient.from_connection_string(
    conn_str=EVENTHUB_CONNECTION_STRING,
    consumer_group="$Default",  # Default consumer group
    eventhub_name=EVENTHUB_NAME
)

with client:
    try:
        print("Starting to receive messages...")
        client.receive(
            on_event=process_message,
            starting_position="-1"  # Start from the beginning of the stream
        )
    except KeyboardInterrupt:
        print("Receiving has been stopped.")
    except Exception as e:
        print(f"An error occurred: {e}")