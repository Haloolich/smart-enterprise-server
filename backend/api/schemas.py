
from datetime import datetime

from pydantic import BaseModel, ConfigDict


# Дані для створення пристрою
class DeviceCreate(BaseModel):
    device_code: str
    name: str
    device_type: str
    location: str | None = None
    connection_type: str = "virtual"


# Дані пристрою у відповіді
class DeviceResponse(BaseModel):
    id: int
    device_code: str
    name: str
    device_type: str
    location: str | None
    connection_type: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Дані для запису показника
class ReadingCreate(BaseModel):
    device_code: str
    sensor_type: str
    value: float
    unit: str


# Показник у відповіді
class ReadingResponse(BaseModel):
    id: int
    device_id: int
    sensor_type: str
    value: float
    unit: str
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Створення правила автоматизації
class RuleCreate(BaseModel):
    name: str
    sensor_type: str
    operator: str
    threshold: float
    action: str
    description: str | None = None


# Відповідь із даними правила
class RuleResponse(BaseModel):
    id: int
    name: str
    sensor_type: str
    operator: str
    threshold: float
    action: str
    description: str | None
    enabled: bool

    model_config = ConfigDict(from_attributes=True)


# Відповідь із даними автоматичної події
class EventResponse(BaseModel):
    id: int
    rule_id: int
    sensor_type: str
    value: float
    action: str
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
