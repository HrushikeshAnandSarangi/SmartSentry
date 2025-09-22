import time
import json
import pandas as pd
import paho.mqtt.client as mqtt
import os

# --- Configuration ---
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "sensors/raw_data"
DATA_DIR = "data"  # Directory containing the data files
DATASETS = ["test_FD001", "test_FD002", "test_FD003", "test_FD004"]  # List of datasets to stream
STREAM_INTERVAL = 0.5  # seconds

# --- CMAPSS Dataset Column Names ---
columns = ['unit_number', 'time_in_cycles', 'setting_1', 'setting_2', 'setting_3']
columns += [f'sensor_{i}' for i in range(1, 22)]

def on_connect(client, userdata, flags, rc, properties=None):
    """Callback for when the client connects to the broker."""
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}\n")

def create_mqtt_client():
    """Creates and configures an MQTT client."""
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    return client

def main():
    """Main function to read data from multiple files and stream it via MQTT."""
    print("--- Starting Data Simulator ---")
    
    mqtt_client = create_mqtt_client()
    mqtt_client.loop_start()  # Start network loop in background
    
    try:
        # Loop indefinitely to provide a continuous stream
        while True:
            for dataset_id in DATASETS:
                data_file_path = os.path.join(DATA_DIR, f"train_{dataset_id}.txt")
                
                print(f"\n--- Loading data from {data_file_path} ---")
                try:
                    df = pd.read_csv(data_file_path, sep='\s+', header=None, names=columns)
                except FileNotFoundError:
                    print(f"Warning: Data file not found at {data_file_path}. Skipping.")
                    continue

                print(f"--- Starting data stream for dataset {dataset_id} ---")
                for _, row in df.iterrows():
                    # Convert the row to a dictionary
                    payload = row.to_dict()
                    # Add the dataset identifier to the payload
                    payload['dataset'] = dataset_id
                    
                    # Publish the JSON string
                    mqtt_client.publish(MQTT_TOPIC, json.dumps(payload))
                    
                    print(f"Published cycle {int(payload['time_in_cycles'])} for unit {int(payload['unit_number'])} from dataset {dataset_id}")
                    
                    # Wait for the specified interval
                    time.sleep(STREAM_INTERVAL)
            
            print("\n--- Completed all datasets. Restarting stream cycle. ---")

    except KeyboardInterrupt:
        print("\nStream stopped by user.")
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print("Disconnected from MQTT Broker.")

if __name__ == '__main__':
    main()