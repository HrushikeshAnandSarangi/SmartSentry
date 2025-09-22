import json
import random
import os
import paho.mqtt.client as mqtt
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.preprocessing import StandardScaler

# --- MQTT Configuration ---
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
SUB_TOPIC = "sensors/raw_data"
ENRICHED_TOPIC = "sensors/enriched_data"
PUB_TOPIC = "alerts/anomaly"

# --- Model and Data Configuration ---
PHASES = ['startup', 'steady', 'shutdown']
phase_models = {}
phase_scalers = {}

THRESHOLDS = {
    'startup': 0.50,
    'steady': 0.37,
    'shutdown': 0.52
}

FEATURE_COLS = (
    ['setting_1', 'setting_2', 'setting_3'] + 
    [f'sensor_{i}' for i in range(1, 22)] + 
    ['recon_error', 'anomaly']
)

def load_models_and_scalers():
    """Loads the autoencoder models and scalers for each phase from the current directory."""
    print("Loading phase-aware models and scalers...")
    for phase in PHASES:
        try:
            model_path = f"autoencoder_{phase}.h5"
            phase_models[phase] = tf.keras.models.load_model(model_path, compile=False)

            scaler_path = f"scaler_{phase}.pkl"
            phase_scalers[phase] = joblib.load(scaler_path)
            
        except IOError as e:
            print(f"Error loading files for phase '{phase}': {e}")
            print("Please ensure all .h5 and .pkl files are in the same directory as this script.")
            exit()
            
    print("✅ Models and scalers loaded successfully.")

def identify_phase(data):
    """
    Identifies the operational phase based on the cycle number.
    This is a refined heuristic adapted for streaming from the notebook's logic.
    """
    cycle = data.get('time_in_cycles', 0)
    
    # --- FIX: Refined heuristic based on typical cycle behavior ---
    if cycle <= 30: # Early cycles are typically startup
        return "startup"
    elif cycle > 175: # Later cycles are typically shutdown
        return "shutdown"
    else: # Normal operational range
        return "steady"

def detect_anomaly(data, phase):
    """Detects anomalies using the appropriate phase-aware autoencoder."""
    print(f"Analyzing for phase: {phase.upper()}...")
    
    model = phase_models.get(phase)
    scaler = phase_scalers.get(phase)
    threshold = THRESHOLDS.get(phase)
    
    if not all([model, scaler, threshold]):
        print(f"Warning: No model, scaler, or threshold found for phase '{phase}'. Skipping anomaly detection.")
        return False

    try:
        data['recon_error'] = 0.0
        data['anomaly'] = False
        
        input_df = pd.DataFrame([data])[FEATURE_COLS]
        X_scaled = scaler.transform(input_df)
        reconstruction = model.predict(X_scaled, verbose=0)
        
        # Calculate loss on the original 24 features only
        loss = np.mean(np.square(X_scaled[:, :24] - reconstruction[:, :24]), axis=1)[0]
        
        print(f"Reconstruction Error: {loss:.4f} | Threshold: {threshold}")
        return loss > threshold
        
    except Exception as e:
        print(f"Error during anomaly detection for phase '{phase}': {e}")
        return False

def predict_failure_type(data):
    """Placeholder for a failure type prediction model."""
    print("Predicting failure type...")
    failures = ["HDC Failure", "Fan Failure", "Overheating", "Pressure Drop"]
    return random.choice(failures)

def on_connect(client, userdata, flags, rc, properties=None):
    """Callback for when the client connects to the MQTT broker."""
    if rc == 0:
        print("Anomaly Predictor connected to MQTT Broker!")
        client.subscribe(SUB_TOPIC)
        print(f"Subscribed to topic: {SUB_TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}\n")

def on_message(client, userdata, msg):
    """Callback for when a message is received from the subscribed topic."""
    try:
        payload = json.loads(msg.payload.decode())
        
        payload['time_in_cycles'] = payload.get('cycle', payload.get('time_in_cycles'))
        payload['unit_number'] = payload.get('engine_id', payload.get('unit_number'))
        
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
    """Main function to initialize and run the MQTT client."""
    if not os.path.exists("autoencoder_steady.h5"):
        print("Error: Model files not found. Ensure .h5 and .pkl files are in the same directory as the script.")
        return

    load_models_and_scalers()
    
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except ConnectionRefusedError:
        print(f"Connection to MQTT broker at {MQTT_BROKER}:{MQTT_PORT} failed. Is it running?")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()