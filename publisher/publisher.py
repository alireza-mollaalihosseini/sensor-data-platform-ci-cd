import time
import json
import random
import paho.mqtt.client as mqtt

broker = "mosquitto"
port = 1883
topic = "sensors/data"

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"✅ Connected to broker at {broker}:{port}")
    else:
        print(f"❌ Failed to connect, return code {rc}")
        exit(1)

client = mqtt.Client()
client.on_connect = on_connect

client.connect(broker, port)
client.loop_start()  # Starts a background thread to manage connection

print("📡 Starting sensor data simulation...")

try:
    while True:
        data = {
            "device_id": f"sensor-{random.randint(1, 11)}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": round(random.uniform(20, 100), 2),
            "co2": round(random.uniform(300, 2000), 2),
            "gas": round(random.uniform(10, 200), 2),
            "smoke": round(random.uniform(5, 70), 2),
            "battery_level": round(random.uniform(20, 100), 2)
        }

        payload = json.dumps(data)
        result = client.publish(topic, payload)

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"✅ Sent: {payload}")
        else:
            print(f"❌ Failed to send message: {payload}")

        time.sleep(2)

except KeyboardInterrupt:
    print("🛑 Stopping simulation...")
    client.loop_stop()
