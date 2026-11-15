
import json
import time

import paho.mqtt.client as mqtt


client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="rule_engine_test"
)

client.connect("127.0.0.1", 1883, 60)
client.loop_start()

time.sleep(1)

test_readings = [
    {
        "device_code": "VIRTUAL_HUB_01",
        "sensor_type": "temperature",
        "value": 30,
        "unit": "°C"
    },
    {
        "device_code": "VIRTUAL_HUB_01",
        "sensor_type": "gas",
        "value": 450,
        "unit": "ppm"
    },
    {
        "device_code": "VIRTUAL_HUB_01",
        "sensor_type": "light",
        "value": 100,
        "unit": "lux"
    }
]

try:
    for reading in test_readings:

        client.publish(
            "enterprise/sensors/reading",
            json.dumps(reading),
            qos=1
        ).wait_for_publish()

        print(
            f"Надіслано: {reading['sensor_type']} = "
            f"{reading['value']} {reading['unit']}"
        )

        time.sleep(1)

finally:
    client.loop_stop()
    client.disconnect()

print("Тестування правил завершено!")
