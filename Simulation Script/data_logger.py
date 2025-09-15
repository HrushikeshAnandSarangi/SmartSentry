import json
import psycopg2
import paho.mqtt.client as mqtt

# --- Configuration ---
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
SENSOR_TOPIC = "sensors/enriched_data"
ALERT_TOPIC = "alerts/anomaly"

DB_HOST = "localhost"
DB_NAME = "asset_data"
DB_USER = "sentry_user"
DB_PASS = "your_password" # <-- IMPORTANT: Use your actual password

def on_connect(client, userdata, flags, rc, properties=None):
    """Callback for when the client connects."""
    if rc == 0:
        print("Data Logger connected to MQTT Broker!")
        # Subscribe to both topics
        client.subscribe(SENSOR_TOPIC)
        client.subscribe(ALERT_TOPIC)
        print(f"Subscribed to {SENSOR_TOPIC} and {ALERT_TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}\n")

def on_message(client, userdata, msg):
    """Callback that handles messages from all topics."""
    try:
        payload = json.loads(msg.payload.decode())
        
        # Route the message based on its topic
        if msg.topic == SENSOR_TOPIC:
            print(f"Received sensor data for unit {payload.get('unit_number')}")
            insert_sensor_data(payload)
        elif msg.topic == ALERT_TOPIC:
            print(f"--- Received ANOMALY ALERT for unit {payload.get('unit_number')} ---")
            insert_alert_data(payload)
            
    except Exception as e:
        print(f"An error occurred in on_message: {e}")

def get_db_connection():
    """Establishes and returns a database connection."""
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)

def insert_sensor_data(data):
    """Inserts a new sensor reading into the sensor_readings table."""
    sql = """INSERT INTO sensor_readings(phase, unit_number, time_in_cycles, setting_1, setting_2, setting_3,
                sensor_1, sensor_2, sensor_3, sensor_4, sensor_5, sensor_6, sensor_7, sensor_8, sensor_9, 
                sensor_10, sensor_11, sensor_12, sensor_13, sensor_14, sensor_15, sensor_16, sensor_17, 
                sensor_18, sensor_19, sensor_20, sensor_21
            ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                      %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    values = (data.get('phase'), data.get('unit_number'), data.get('time_in_cycles'), data.get('setting_1'), 
              data.get('setting_2'), data.get('setting_3'), data.get('sensor_1'), data.get('sensor_2'), 
              data.get('sensor_3'), data.get('sensor_4'), data.get('sensor_5'), data.get('sensor_6'), 
              data.get('sensor_7'), data.get('sensor_8'), data.get('sensor_9'), data.get('sensor_10'), 
              data.get('sensor_11'), data.get('sensor_12'), data.get('sensor_13'), data.get('sensor_14'), 
              data.get('sensor_15'), data.get('sensor_16'), data.get('sensor_17'), data.get('sensor_18'), 
              data.get('sensor_19'), data.get('sensor_20'), data.get('sensor_21'))
    
    execute_query(sql, values)

def insert_alert_data(data):
    """Inserts a new alert into the alerts table."""
    sql = """INSERT INTO alerts(unit_number, time_in_cycles, phase) VALUES(%s, %s, %s);"""
    values = (data.get('unit_number'), data.get('time_in_cycles'), data.get('phase'))
    execute_query(sql, values)

def execute_query(sql, values):
    """Executes a given SQL query with its values."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(sql, values)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error on execute_query: {error}")
    finally:
        if conn is not None:
            conn.close()

def main():
    """Main function to set up MQTT client and start listening."""
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == '__main__':
    main()