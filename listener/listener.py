import os
import sys
import json
import paho.mqtt.client as mqtt
import psycopg2
from datetime import datetime

# Add project root to import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from utils.anomaly_detector import is_anomaly
def is_anomaly(data):
    if data["temperature"] > 75 or data["co2"] > 1000:
        return True
    return False


DATA_DIR = os.environ.get("DATA_DIR", "/app/data")
os.makedirs(DATA_DIR, exist_ok=True)  # Ensure the folder exists

def save_to_file(data):
    timestamp = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(DATA_DIR, f"anomalies_{timestamp}.csv")
    
    with open(file_path, 'a') as f:
        f.write(f"{data['device_id']},{data['co2']},{data['gas']},{data['smoke']},{data['temperature']},{data['battery_level']},{data['timestamp']}\n")

# PostgreSQL connection setup
try:
    conn = psycopg2.connect(
        dbname="sensordata",
        user="sensoruser",
        password="sensorpass",
        host="db",  # matches docker-compose service name
        port="5432"
    )
    cursor = conn.cursor()
    print("✅ Connected to PostgreSQL")
except Exception as e:
    print("❌ Failed to connect to PostgreSQL:", e)
    sys.exit(1)

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Connected to MQTT broker (listener)")
        client.subscribe("sensors/data")
    else:
        print("❌ Listener failed to connect. Return code:", rc)

def save_to_db(data):
    cursor.execute("""
        INSERT INTO sensor_readings (device_id, co2, gas, smoke, temperature, battery_level, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        int(data["device_id"].split("-")[1]),
        data["co2"],
        data["gas"],
        data["smoke"],
        data["temperature"],
        data["battery_level"],
        data["timestamp"]
    ))
    conn.commit()

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print("📥 Received:", data)

        if is_anomaly(data):
            print("⚠️  Anomaly Detected!")
            save_to_db(data)
            save_to_file(data)  # 👈 new addition
            print("💾 Saved to PostgreSQL and logged to file")

    except Exception as e:
        print("❌ Error handling message:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("mosquitto", 1883)
print("🚀 Listening for sensor data on port 1883...")
client.loop_forever()
