
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
    Text
)
from sqlalchemy.orm import relationship

from backend.database.database import Base
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import Column, Integer, String, DateTime, Boolean


# Таблиця пристроїв
class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)

    device_code = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    name = Column(String, nullable=False)
    device_type = Column(String, nullable=False)

    location = Column(String, nullable=True)

    connection_type = Column(
        String,
        default="virtual",
        nullable=False
    )

    status = Column(
        String,
        default="offline",
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    readings = relationship(
        "SensorReading",
        back_populates="device"
    )


# Таблиця показників датчиків
class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)

    device_id = Column(
        Integer,
        ForeignKey("devices.id"),
        nullable=False
    )

    sensor_type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)

    recorded_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    device = relationship(
        "Device",
        back_populates="readings"
    )

# Таблиця правил автоматизації
class AutomationRule(Base):
    __tablename__ = "automation_rules"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    sensor_type = Column(String, nullable=False)

    operator = Column(String, nullable=False)
    threshold = Column(Float, nullable=False)

    action = Column(String, nullable=False)
    description = Column(String, nullable=True)

    enabled = Column(
        Boolean,
        default=True,
        nullable=False
    )

    last_condition_state = Column(
        Boolean,
        default=False,
        nullable=False
    )



# Журнал автоматичних подій
class AutomationEvent(Base):
    __tablename__ = "automation_events"

    id = Column(Integer, primary_key=True, index=True)

    rule_id = Column(
        Integer,
        ForeignKey("automation_rules.id"),
        nullable=False
    )

    sensor_type = Column(String, nullable=False)
    value = Column(Float, nullable=False)

    action = Column(String, nullable=False)
    message = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    rule = relationship("AutomationRule")


# Налаштування режиму керування системою
class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True)
    control_mode = Column(
        String,
        default="automatic",
        nullable=False
    )


# Таблиця виконавчих пристроїв
class Actuator(Base):
    __tablename__ = "actuators"

    id = Column(Integer, primary_key=True, index=True)

    code = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    name = Column(String, nullable=False)

    actuator_type = Column(String, nullable=False)

    state = Column(
        String,
        default="off",
        nullable=False
    )

    connection_type = Column(
        String,
        default="virtual",
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )


# Журнал команд виконавчим пристроям
class DeviceCommand(Base):
    __tablename__ = "device_commands"

    id = Column(Integer, primary_key=True, index=True)

    actuator_id = Column(
        Integer,
        ForeignKey("actuators.id"),
        nullable=False
    )

    rule_id = Column(
        Integer,
        ForeignKey("automation_rules.id"),
        nullable=True
    )

    source = Column(String, nullable=False)

    command = Column(String, nullable=False)

    result = Column(String, nullable=False)

    mqtt_topic = Column(String, nullable=False)

    payload = Column(Text, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    actuator = relationship("Actuator")
    rule = relationship("AutomationRule")

# Журнал адміністративних дій
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    action = Column(
        String,
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    entity_type = Column(
        String,
        nullable=True
    )

    entity_id = Column(
        Integer,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
# Користувачі системи
class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(50),
        default="user",
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )