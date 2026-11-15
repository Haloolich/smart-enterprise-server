
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Boolean
)
from sqlalchemy.orm import relationship

from backend.database.database import Base


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
