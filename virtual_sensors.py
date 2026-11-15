
import json
import random
import time

import paho.mqtt.client as mqtt


# Налаштування MQTT
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "enterprise/sensors/reading"

DEVICE_CODE = "VIRTUAL_HUB_01"


# Генерація показників датчиків
def generate_sensor_data():

    # Температура: 20-30 °C
    temperature = round(random.uniform(20, 30), 1)

    # Вологість: 35-70 %
    humidity = round(random.uniform(35, 70), 1)

    # Газ: умовне значення концентрації
    gas = round(random.uniform(100, 500), 1)

    # Освітленість: 50-1000 люкс
    light = round(random.uniform(50, 1000), 1)

    # Рух: 0 - руху немає, 1 - рух виявлено
    motion = random.choice([0, 1])

    readings = [
        {
            "sensor_type": "temperature",
            "value": temperature,
            "unit": "°C"
        },
        {
            "sensor_type": "humidity",
            "value": humidity,
            "unit": "%"
        },
        {
            "sensor_type": "gas",
            "value": gas,
            "unit": "ppm"
        },
        {
            "sensor_type": "light",
            "value": light,
            "unit": "lux"
        },
        {
            "sensor_type": "motion",
            "value": motion,
            "unit": "state"
        }
    ]

    return readings


# Підключення до MQTT
client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="virtual_sensor_generator"
)

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

print("Генератор віртуальних датчиків запущено!")
print("Для зупинки натисни Ctrl + C.")

try:
    while True:

        readings = generate_sensor_data()

        for reading in readings:

            message = {
                "device_code": DEVICE_CODE,
                "sensor_type": reading["sensor_type"],
                "value": reading["value"],
                "unit": reading["unit"]
            }

            payload = json.dumps(message)

            result = client.publish(
                MQTT_TOPIC,
                payload,
                qos=1
            )

            result.wait_for_publish()

            print(
                f"{reading['sensor_type']}: "
                f"{reading['value']} {reading['unit']}"
            )

        print("-" * 40)

        # Інтервал між циклами генерації
        time.sleep(5)

except KeyboardInterrupt:
    print("\nГенератор зупиняється...")

finally:
    client.loop_stop()
    client.disconnect()
    print("Генератор зупинено.")
