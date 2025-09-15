import json
import psycopg2
import paho.mqtt.client as mqtt

# --- Configuration ---
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "sensors/enriched_data" # Subscribes to the enriched topic

DB_HOST = "localhost"
DB_NAME = "asset_data"
DB_USER = "sentry_user"
DB_PASS = "your_password" # <-- IMPORTANT: Use your actual password

def on_connect(client, userdata, flags, rc, properties=None):
    """Callback for when the client connects to the broker."""
    if rc == 0:
        print("Data Logger connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}\n")

def on_message(client, userdata, msg):
    """Callback for when a message is received from the broker."""
    try:
        # Decode the payload from JSON
        payload = json.loads(msg.payload.decode())
        print(f"Received data for unit {payload.get('unit_number')}, phase: {payload.get('phase')}")
        
        # Insert data into the database
        insert_data(payload)
        
    except json.JSONDecodeError:
        print("Error decoding JSON from message.")
    except Exception as e:
        print(f"An error occurred: {e}")

def insert_data(data):
    """Connects to the DB and inserts a new sensor reading."""
    # Updated SQL to include the 'phase' column
    sql = """INSERT INTO sensor_readings(
                phase, unit_number, time_in_cycles, setting_1, setting_2, setting_3,
                sensor_1, sensor_2, sensor_3, sensor_4, sensor_5, sensor_6,
                sensor_7, sensor_8, sensor_9, sensor_10, sensor_11, sensor_12,
                sensor_13, sensor_14, sensor_15, sensor_16, sensor_17, sensor_18,
                sensor_19, sensor_20, sensor_21
            ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                      %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    
    conn = None
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        
        # Create a tuple of values in the correct order for the new SQL statement
        values = (
            data.get('phase'), data.get('unit_number'), data.get('time_in_cycles'),
            data.get('setting_1'), data.get('setting_2'), data.get('setting_3'),
            data.get('sensor_1'), data.get('sensor_2'), data.get('sensor_3'), data.get('sensor_4'),
            data.get('sensor_5'), data.get('sensor_6'), data.get('sensor_7'), data.get('sensor_8'),
            data.get('sensor_9'), data.get('sensor_10'), data.get('sensor_11'), data.get('sensor_12'),
            data.get('sensor_13'), data.get('sensor_14'), data.get('sensor_15'), data.get('sensor_16'),
            data.get('sensor_17'), data.get('sensor_18'), data.get('sensor_19'), data.get('sensor_20'),
            data.get('sensor_21')
        )
        
        cur.execute(sql, values)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
    finally:
        if conn is not None: # Corrected typo from 'nowne'
            conn.close()

def main():
    """Main function to set up MQTT client and start listening."""
    # Use the new Callback API Version to avoid deprecation warnings
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == '__main__':
    main()