
import json
import logging

import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session

from backend.database.database import SessionLocal
from backend.database.models import Device, SensorReading
from backend.rule_engine import evaluate_rules

# Налаштування журналювання
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Налаштування MQTT
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "enterprise/sensors/reading"


# Обробка підключення до брокера
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        logger.info("MQTT: успішне підключення до брокера")

        client.subscribe(MQTT_TOPIC)
        logger.info(f"MQTT: підписка на тему {MQTT_TOPIC}")
    else:
        logger.error(f"MQTT: помилка підключення: {reason_code}")


# Обробка отриманих повідомлень
def on_message(client, userdata, message):
    db: Session = SessionLocal()

    try:
        payload = json.loads(message.payload.decode("utf-8"))

        device_code = payload["device_code"]
        sensor_type = payload["sensor_type"]
        value = float(payload["value"])
        unit = payload["unit"]

        # Шукаємо пристрій у базі даних
        device = db.query(Device).filter(
            Device.device_code == device_code
        ).first()

        if not device:
            logger.warning(
                f"Невідомий пристрій: {device_code}"
            )
            return

        # Створюємо запис показника
        reading = SensorReading(
            device_id=device.id,
            sensor_type=sensor_type,
            value=value,
            unit=unit
        )

        db.add(reading)

        # Перевіряємо правила автоматизації
        triggered_rules = evaluate_rules(
            db,
            sensor_type,
            value
        )

        db.commit()

        for rule_name in triggered_rules:
            logger.warning(
                f"Автоматична дія: {rule_name}"
            )

        logger.info(
            f"Збережено: {device_code}, "
            f"{sensor_type} = {value} {unit}"
        )

    except (ValueError, KeyError, json.JSONDecodeError) as error:
        logger.error(f"Некоректне MQTT-повідомлення: {error}")

    except Exception:
        db.rollback()
        logger.exception("Помилка збереження MQTT-показника")

    finally:
        db.close()


# Створення MQTT-клієнта
mqtt_client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="smart_enterprise_server"
)

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message


# Запуск MQTT-клієнта
def start_mqtt():
    try:
        mqtt_client.connect(
            MQTT_BROKER,
            MQTT_PORT,
            60
        )

        mqtt_client.loop_start()

        logger.info("MQTT-клієнт запущено")

    except Exception:
        logger.exception("Не вдалося запустити MQTT-клієнт")


# Зупинка MQTT-клієнта
def stop_mqtt():
    mqtt_client.loop_stop()
    mqtt_client.disconnect()

    logger.info("MQTT-клієнт зупинено")
