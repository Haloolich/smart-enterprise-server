
import json
import time

import paho.mqtt.client as mqtt


client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="mqtt_test_sender"
)

client.connect("127.0.0.1", 1883, 60)
client.loop_start()

time.sleep(1)

data = {
    "device_code": "ESP32_01",
    "sensor_type": "temperature",
    "value": 24.5,
    "unit": "°C"
}

client.publish(
    "enterprise/sensors/reading",
    json.dumps(data, ensure_ascii=False),
    qos=1
)

time.sleep(1)

client.disconnect()
client.loop_stop()

print("Тестове MQTT-повідомлення надіслано!")
