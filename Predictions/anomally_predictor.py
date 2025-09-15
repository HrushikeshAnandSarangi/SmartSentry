import json
import random
import paho.mqtt.client as mqtt

# --- Configuration ---
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
SUB_TOPIC = "sensors/raw_data"        # Topic for incoming raw data
ENRICHED_TOPIC = "sensors/enriched_data" # Topic for data + phase
PUB_TOPIC = "alerts/anomaly"          # Topic for anomaly alerts

def identify_phase(data):
    """Identifies the operational phase based on sensor settings."""
    setting1 = data.get('setting_1', 0)
    
    if setting1 < 0.001:
        return "startup"
    elif setting1 > 0.002:
        return "shutdown"
    else:
        return "steady_state"

def detect_anomaly(data, phase):
    """Placeholder for the anomaly detection model."""
    print(f"Analyzing for phase: {phase.upper()}. Loading '{phase}_model.pkl'...")
    is_anomaly = random.random() < 0.1 # Dummy: 10% chance of anomaly
    return is_anomaly

def on_connect(client, userdata, flags, rc, properties=None):
    """Callback for when the client connects."""
    if rc == 0:
        print("Engine connected to MQTT Broker!")
        client.subscribe(SUB_TOPIC)
        print(f"Subscribed to topic: {SUB_TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}\n")

def on_message(client, userdata, msg):
    """Callback for when a message is received."""
    try:
        payload = json.loads(msg.payload.decode())
        
        # 1. Identify the operational phase
        phase = identify_phase(payload)
        
        # 2. Enrich the payload with the phase
        payload['phase'] = phase
        
        # 3. Publish the enriched data for the logger/dashboard
        client.publish(ENRICHED_TOPIC, json.dumps(payload))
        
        # 4. Detect anomalies for that phase
        is_anomaly = detect_anomaly(payload, phase)
        
        print(f"Unit {payload['unit_number']} | Cycle {payload['time_in_cycles']} | Phase: {phase} | Anomaly: {is_anomaly}")

        # 5. If an anomaly is found, publish a separate alert
        if is_anomaly:
            alert_payload = {
                "unit_number": payload['unit_number'],
                "time_in_cycles": payload['time_in_cycles'],
                "phase": phase,
                "anomaly_detected": True,
                "original_data": payload 
            }
            client.publish(PUB_TOPIC, json.dumps(alert_payload))
            print(f"--- ANOMALY ALERT PUBLISHED to {PUB_TOPIC} ---")

    except Exception as e:
        print(f"An error occurred in on_message: {e}")

def main():
    """Main function to set up MQTT client."""
    # Use the new Callback API Version to avoid deprecation warnings
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == '__main__':
    main()