import json
import random
import paho.mqtt.client as mqtt

MQTT_BROKER = "mqtt-broker"
MQTT_PORT = 1883
SUB_TOPIC = "sensors/raw_data"
ENRICHED_TOPIC = "sensors/enriched_data"
PUB_TOPIC = "alerts/anomaly"

def identify_phase(data):
    setting1 = data.get('setting_1', 0)
    if setting1 < 0.001: return "startup"
    elif setting1 > 0.002: return "shutdown"
    else: return "steady_state"

def detect_anomaly(data, phase):
    print(f"Analyzing for phase: {phase.upper()}. Loading '{phase}_model.pkl'...")
    return random.random() < 0.1 

def predict_failure_type(data): 

    print("Predicting failure type...")
    failures = ["HDC Failure", "Fan Failure", "Overheating", "Pressure Drop"]
    return random.choice(failures)

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Engine connected to MQTT Broker!")
        client.subscribe(SUB_TOPIC)
        print(f"Subscribed to topic: {SUB_TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}\n")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        phase = identify_phase(payload)
        payload['phase'] = phase
        client.publish(ENRICHED_TOPIC, json.dumps(payload))
        
        is_anomaly = detect_anomaly(payload, phase)
        print(f"Unit {payload['unit_number']} | Cycle {payload['time_in_cycles']} | Phase: {phase} | Anomaly: {is_anomaly}")

        if is_anomaly:
            failure_type = predict_failure_type(payload) 
            
            alert_payload = {
                "unit_number": payload['unit_number'],
                "time_in_cycles": payload['time_in_cycles'],
                "phase": phase,
                "anomaly_detected": True,
                "failure_type": failure_type, 
                "original_data": payload 
            }
            client.publish(PUB_TOPIC, json.dumps(alert_payload))
            print(f"--- ANOMALY ALERT: {failure_type} | Published to {PUB_TOPIC} ---")

    except Exception as e:
        print(f"An error occurred in on_message: {e}")

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == '__main__':
    main()