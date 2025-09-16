import time
import json
import pandas as pd
import paho.mqtt.client as mqtt

# --- Configuration ---
MQTT_BROKER = "mqtt-broker"
MQTT_PORT = 1883
MQTT_TOPIC = "sensors/raw_data"
DATA_FILE = "data/train_FD001.txt"
STREAM_INTERVAL = 1.0  # seconds

# --- CMAPSS Dataset Column Names ---
# As per the dataset documentation
columns = ['unit_number', 'time_in_cycles', 'setting_1', 'setting_2', 'setting_3']
columns += [f'sensor_{i}' for i in range(1, 22)]

def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the broker."""
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}\n")

def create_mqtt_client():
    """Creates and configures an MQTT client."""
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    return client

def main():
    """Main function to read data and stream it via MQTT."""
    print("--- Starting Data Simulator ---")
    
    # Create MQTT client
    mqtt_client = create_mqtt_client()
    mqtt_client.loop_start()  # Start network loop in background
    
    # Load the dataset
    print(f"Loading data from {DATA_FILE}...")
    try:
        df = pd.read_csv(DATA_FILE, sep='\s+', header=None, names=columns)
    except FileNotFoundError:
        print(f"Error: Data file not found at {DATA_FILE}")
        return

    print("Starting data stream...")
    try:
        for index, row in df.iterrows():
            # Convert the row to a dictionary and then to a JSON string
            payload = row.to_dict()
            mqtt_client.publish(MQTT_TOPIC, json.dumps(payload))
            
            print(f"Published cycle {int(payload['time_in_cycles'])} for unit {int(payload['unit_number'])}")
            
            # Wait for the specified interval
            time.sleep(STREAM_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nStream stopped by user.")
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print("Disconnected from MQTT Broker.")

if __name__ == '__main__':
    main()