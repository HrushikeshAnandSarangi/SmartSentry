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
# Set to 'localhost' for local testing, or the broker's hostname/IP
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
SUB_TOPIC = "sensors/raw_data"
ENRICHED_TOPIC = "sensors/enriched_data"
PUB_TOPIC = "alerts/anomaly"

# --- Model and Data Configuration ---
PHASES = ['startup', 'steady', 'shutdown']
phase_models = {}
phase_scalers = {}

# Anomaly thresholds calculated from the training notebook (mean + 3*std_dev of reconstruction error)
# These are pre-calculated for efficiency in a streaming environment.
THRESHOLDS = {
    'startup': 0.50,
    'steady': 0.37,
    'shutdown': 0.52
}

# Feature columns the models were trained on
FEATURE_COLS = ['setting_1', 'setting_2', 'setting_3'] + [f'sensor_{i}' for i in range(1, 22)]

def load_models_and_scalers():
    """Loads the autoencoder models and scalers for each phase from the current directory."""
    print("Loading phase-aware models and scalers...")
    for phase in PHASES:
        try:
            # Load the pre-trained model directly from the current directory
            model_path = f"autoencoder_{phase}.h5"
            # Use compile=False to avoid errors when loading models saved with a different Keras version
            phase_models[phase] = tf.keras.models.load_model(model_path, compile=False)

            # Load the corresponding scaler
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
    This is a heuristic adapted for streaming from the notebook's logic.
    """
    cycle = data.get('time_in_cycles', 0)
    
    # Heuristic based on typical cycle behavior observed in the training dataset
    if cycle <= 40: # Early cycles
        return "startup"
    elif cycle > 160: # Approaching end-of-life
        return "shutdown"
    else: # Normal operational range
        return "steady"

def detect_anomaly(data, phase):
    """
    Detects anomalies using the appropriate phase-aware autoencoder.
    """
    print(f"Analyzing for phase: {phase.upper()}...")
    
    # Select the correct model, scaler, and threshold for the current phase
    model = phase_models.get(phase)
    scaler = phase_scalers.get(phase)
    threshold = THRESHOLDS.get(phase)
    
    if not all([model, scaler, threshold]):
        print(f"Warning: No model, scaler, or threshold found for phase '{phase}'. Skipping anomaly detection.")
        return False

    try:
        # Prepare the incoming data into a DataFrame with the correct column order
        input_df = pd.DataFrame([data])[FEATURE_COLS]
        
        # Scale the features using the phase-specific scaler
        X_scaled = scaler.transform(input_df)
        
        # Get the reconstruction from the autoencoder
        reconstruction = model.predict(X_scaled, verbose=0)
        
        # Calculate the Mean Squared Error (reconstruction loss)
        loss = np.mean(np.square(X_scaled - reconstruction), axis=1)[0]
        
        print(f"Reconstruction Error: {loss:.4f} | Threshold: {threshold}")
        return loss > threshold
        
    except Exception as e:
        print(f"Error during anomaly detection for phase '{phase}': {e}")
        return False

def predict_failure_type(data):
    """
    Placeholder for a failure type prediction model.
    Currently returns a random failure type for demonstration.
    """
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
        
        # Standardize keys to match notebook columns ('cycle' and 'engine_id')
        payload['time_in_cycles'] = payload.get('cycle', payload.get('time_in_cycles'))
        payload['unit_number'] = payload.get('engine_id', payload.get('unit_number'))
        
        # 1. Identify the operational phase
        phase = identify_phase(payload)
        payload['phase'] = phase
        client.publish(ENRICHED_TOPIC, json.dumps(payload))
        
        # 2. Detect anomalies using the phase-aware model
        is_anomaly = detect_anomaly(payload, phase)
        print(f"Unit {payload['unit_number']} | Cycle {payload['time_in_cycles']} | Phase: {phase} | Anomaly: {is_anomaly}")

        # 3. If an anomaly is found, predict failure type and publish an alert
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
    # Check for one of the model files to ensure they exist before starting
    if not os.path.exists("autoencoder_steady.h5"):
        print("Error: Model files not found. Ensure .h5 and .pkl files are in the same directory as the script.")
        return

    # Load models and scalers once at the start
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