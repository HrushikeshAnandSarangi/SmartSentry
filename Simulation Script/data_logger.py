import json
import psycopg2
import paho.mqtt.client as mqtt

# --- Configuration ---
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "sensors/raw_data"

DB_HOST = "localhost"
DB_NAME = "asset_data"
DB_USER = "sentry_user"
DB_PASS = "your_password" # <-- IMPORTANT: Change this!

def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the broker."""
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}\n")

def on_message(client, userdata, msg):
    """Callback for when a message is received from the broker."""
    try:
        # Decode the payload from JSON
        payload = json.loads(msg.payload.decode())
        print(f"Received data for unit {int(payload['unit_number'])}, cycle {int(payload['time_in_cycles'])}")
        
        # Insert data into the database
        insert_data(payload)
        
    except json.JSONDecodeError:
        print("Error decoding JSON from message.")
    except Exception as e:
        print(f"An error occurred: {e}")

def insert_data(data):
    """Connects to the DB and inserts a new sensor reading."""
    sql = """INSERT INTO sensor_readings(
                unit_number, time_in_cycles, setting_1, setting_2, setting_3,
                sensor_1, sensor_2, sensor_3, sensor_4, sensor_5, sensor_6,
                sensor_7, sensor_8, sensor_9, sensor_10, sensor_11, sensor_12,
                sensor_13, sensor_14, sensor_15, sensor_16, sensor_17, sensor_18,
                sensor_19, sensor_20, sensor_21
            ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    
    conn = None
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        
        # Create a tuple of values from the data dictionary
        values = tuple(data[key] for key in sorted(data.keys()))
        
        # Execute the SQL command
        cur.execute(sql, values)
        
        # Commit the transaction
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
    finally:
        if conn is not nowne:
            conn.close()

def main():
    """Main function to set up MQTT client and start listening."""
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    # Blocking call that processes network traffic, dispatches callbacks, and handles reconnecting.
    client.loop_forever()

if __name__ == '__main__':
    main()