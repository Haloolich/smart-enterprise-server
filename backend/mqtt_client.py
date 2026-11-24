
import json
import logging
import math

from datetime import datetime, timezone

import paho.mqtt.client as mqtt

from sqlalchemy.orm import Session

from backend.database.database import SessionLocal

from backend.database.models import (
    Device,
    SensorReading,
    Actuator,
    DeviceCommand
)

from backend.rule_engine import evaluate_rules


# Налаштування журналювання
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


# Налаштування MQTT
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883

MQTT_SENSOR_TOPIC = "enterprise/sensors/reading"

MQTT_COMMAND_TOPIC = "enterprise/actuators/command"


# Відповідність правил виконавчим пристроям
ACTION_MAPPING = {
    "turn_on_ventilation": {
        "actuator_code": "VENTILATION_01",
        "command": "turn_on"
    },

    "turn_on_light": {
        "actuator_code": "LIGHT_01",
        "command": "turn_on"
    },

    "send_alert": {
        "actuator_code": "ALERT_01",
        "command": "send_alert"
    }
}


# Створення віртуальних виконавчих пристроїв
def initialize_actuators():

    db = SessionLocal()

    actuators = [
        {
            "code": "VENTILATION_01",
            "name": "Система вентиляції",
            "actuator_type": "ventilation"
        },
        {
            "code": "LIGHT_01",
            "name": "Система освітлення",
            "actuator_type": "lighting"
        },
        {
            "code": "ALERT_01",
            "name": "Система сповіщень",
            "actuator_type": "notification"
        }
    ]

    try:
        for item in actuators:

            existing = db.query(Actuator).filter(
                Actuator.code == item["code"]
            ).first()

            if not existing:

                actuator = Actuator(
                    code=item["code"],
                    name=item["name"],
                    actuator_type=item["actuator_type"],
                    state="off",
                    connection_type="virtual"
                )

                db.add(actuator)

        db.commit()

        logger.info(
            "Віртуальні виконавчі пристрої перевірено"
        )

    except Exception:
        db.rollback()
        logger.exception(
            "Помилка створення виконавчих пристроїв"
        )

    finally:
        db.close()


# Надсилання команди виконавчому пристрою
def send_actuator_command(
    db: Session,
    rule_info: dict
):

    action = rule_info["action"]

    mapping = ACTION_MAPPING.get(action)

    if not mapping:

        logger.warning(
            f"Невідома автоматична дія: {action}"
        )

        return

    actuator = db.query(Actuator).filter(
        Actuator.code == mapping["actuator_code"]
    ).first()

    if not actuator:

        logger.error(
            f"Не знайдено пристрій: "
            f"{mapping['actuator_code']}"
        )

        return

    command = mapping["command"]

    payload = {
        "actuator_code": actuator.code,
        "command": command,
        "source": "automatic",
        "rule_id": rule_info["id"],
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat()
    }

    payload_json = json.dumps(
        payload,
        ensure_ascii=False
    )

    result = "not_connected"

    # Публікуємо команду через MQTT
    if mqtt_client.is_connected():

        try:
            publish_info = mqtt_client.publish(
                MQTT_COMMAND_TOPIC,
                payload_json,
                qos=1
            )

            if publish_info.rc == mqtt.MQTT_ERR_SUCCESS:
                result = "queued"

                # Оновлюємо стан віртуального пристрою
                if command == "turn_on":
                    actuator.state = "on"

                elif command == "turn_off":
                    actuator.state = "off"

                actuator.updated_at = datetime.now(
                    timezone.utc
                )

                logger.info(
                    f"MQTT-команду поставлено в чергу: "
                    f"{actuator.code} -> {command}"
                )

            else:
                result = "publish_error"

                logger.error(
                    f"Помилка публікації MQTT: "
                    f"{publish_info.rc}"
                )

        except Exception:
            result = "publish_error"

            logger.exception(
                "Помилка надсилання MQTT-команди"
            )

    else:

        logger.warning(
            "MQTT-брокер недоступний. "
            "Команду не надіслано."
        )

    # Зберігаємо історію команди
    command_record = DeviceCommand(
        actuator_id=actuator.id,
        rule_id=rule_info["id"],
        source="automatic",
        command=command,
        result=result,
        mqtt_topic=MQTT_COMMAND_TOPIC,
        payload=payload_json
    )

    db.add(command_record)
    db.commit()

def send_manual_actuator_command(
    db: Session,
    actuator: Actuator,
    command: str
):
    payload = {
        "actuator_code": actuator.code,
        "command": command,
        "source": "manual",
        "rule_id": None,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat()
    }

    payload_json = json.dumps(
        payload,
        ensure_ascii=False
    )

    result = "not_connected"

    # Публікуємо команду через MQTT
    if mqtt_client.is_connected():

        try:
            publish_info = mqtt_client.publish(
                MQTT_COMMAND_TOPIC,
                payload_json,
                qos=1
            )

            if publish_info.rc == mqtt.MQTT_ERR_SUCCESS:
                result = "queued"

                # Оновлюємо стан віртуального пристрою
                if command == "turn_on":
                    actuator.state = "on"

                elif command == "turn_off":
                    actuator.state = "off"

                actuator.updated_at = datetime.now(
                    timezone.utc
                )

                logger.info(
                    f"Ручну MQTT-команду поставлено в чергу: "
                    f"{actuator.code} -> {command}"
                )

            else:
                result = "publish_error"

                logger.error(
                    f"Помилка публікації MQTT: "
                    f"{publish_info.rc}"
                )

        except Exception:
            result = "publish_error"

            logger.exception(
                "Помилка надсилання ручної MQTT-команди"
            )

    else:
        logger.warning(
            "MQTT-брокер недоступний. "
            "Ручну команду не надіслано."
        )

    # Зберігаємо історію команди
    command_record = DeviceCommand(
        actuator_id=actuator.id,
        rule_id=None,
        source="manual",
        command=command,
        result=result,
        mqtt_topic=MQTT_COMMAND_TOPIC,
        payload=payload_json
    )

    db.add(command_record)
    db.commit()

    return result

# Обробка підключення до брокера
def on_connect(
    client,
    userdata,
    flags,
    reason_code,
    properties
):

    if reason_code == 0:

        logger.info(
            "MQTT: успішне підключення до брокера"
        )

        client.subscribe(MQTT_SENSOR_TOPIC)

        logger.info(
            f"MQTT: підписка на тему "
            f"{MQTT_SENSOR_TOPIC}"
        )

    else:

        logger.error(
            f"MQTT: помилка підключення: {reason_code}"
        )


# Обробка отриманих повідомлень

# Обробка отриманих повідомлень
def on_message(client, userdata, message):

    db: Session = SessionLocal()

    try:
        # Декодування та перевірка JSON
        payload = json.loads(
            message.payload.decode("utf-8")
        )

        # Перевіряємо, що отримано саме JSON-об'єкт
        if not isinstance(payload, dict):
            raise ValueError("Повідомлення має бути JSON-об'єктом")

        # Перевіряємо обов'язкові поля
        device_code = payload.get("device_code")
        sensor_type = payload.get("sensor_type")
        raw_value = payload.get("value")
        unit = payload.get("unit", "")

        if not isinstance(device_code, str) or not device_code.strip():
            raise ValueError("Некоректний device_code")

        if not isinstance(sensor_type, str) or not sensor_type.strip():
            raise ValueError("Некоректний sensor_type")

        if raw_value is None or isinstance(raw_value, bool):
            raise ValueError("Некоректне значення датчика")

        # Перетворення значення на число
        value = float(raw_value)

        # Перевірка на NaN та нескінченність
        if not math.isfinite(value):
            raise ValueError("Значення датчика має бути скінченним числом")

        if not isinstance(unit, str):
            raise ValueError("Некоректна одиниця вимірювання")

        device_code = device_code.strip()
        sensor_type = sensor_type.strip()
        unit = unit.strip()

        # Пошук пристрою
        device = db.query(Device).filter(
            Device.device_code == device_code
        ).first()

        if not device:
            logger.warning(
                f"Невідомий пристрій: {device_code}"
            )
            return

        # Збереження показника
        reading = SensorReading(
            device_id=device.id,
            sensor_type=sensor_type,
            value=value,
            unit=unit
        )

        db.add(reading)

        # Перевірка автоматичних правил
        triggered_rules = evaluate_rules(
            db,
            sensor_type,
            value
        )

        # Зберігаємо показник та події правил
        db.commit()

        # Надсилаємо команди для правил, що спрацювали
        for rule_info in triggered_rules:

            logger.warning(
                f"Автоматична дія: "
                f"{rule_info['name']}"
            )

            send_actuator_command(
                db,
                rule_info
            )

        logger.info(
            f"Збережено: {device_code}, "
            f"{sensor_type} = {value} {unit}"
        )

    except (
        ValueError,
        KeyError,
        json.JSONDecodeError,
        UnicodeDecodeError
    ) as error:

        db.rollback()

        logger.error(
            f"Некоректне MQTT-повідомлення: {error}"
        )

    except Exception:

        db.rollback()

        logger.exception(
            "Помилка обробки MQTT-повідомлення"
        )

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

        initialize_actuators()

        mqtt_client.connect(
            MQTT_BROKER,
            MQTT_PORT,
            60
        )

        mqtt_client.loop_start()

        logger.info(
            "MQTT-клієнт запущено"
        )

    except Exception:

        logger.exception(
            "Не вдалося запустити MQTT-клієнт"
        )


# Зупинка MQTT-клієнта
def stop_mqtt():

    mqtt_client.loop_stop()

    mqtt_client.disconnect()

    logger.info(
        "MQTT-клієнт зупинено"
    )
