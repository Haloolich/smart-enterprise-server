
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import Device, SensorReading
from backend.api.schemas import (
    DeviceCreate,
    DeviceResponse,
    ReadingCreate,
    ReadingResponse
)
from backend.database.models import AutomationRule, AutomationEvent
from backend.api.schemas import RuleCreate, RuleResponse, EventResponse


router = APIRouter(prefix="/api", tags=["Database"])


# Реєстрація нового пристрою
@router.post("/devices", response_model=DeviceResponse)
def create_device(
    device_data: DeviceCreate,
    db: Session = Depends(get_db)
):
    existing_device = db.query(Device).filter(
        Device.device_code == device_data.device_code
    ).first()

    if existing_device:
        raise HTTPException(
            status_code=409,
            detail="Пристрій з таким кодом вже існує"
        )

    new_device = Device(**device_data.model_dump())

    db.add(new_device)
    db.commit()
    db.refresh(new_device)

    return new_device


# Отримання списку пристроїв
@router.get("/devices", response_model=list[DeviceResponse])
def get_devices(db: Session = Depends(get_db)):
    return db.query(Device).all()


# Додавання показника датчика
@router.post("/readings", response_model=ReadingResponse)
def create_reading(
    reading_data: ReadingCreate,
    db: Session = Depends(get_db)
):
    device = db.query(Device).filter(
        Device.device_code == reading_data.device_code
    ).first()

    if not device:
        raise HTTPException(
            status_code=404,
            detail="Пристрій не знайдено"
        )

    new_reading = SensorReading(
        device_id=device.id,
        sensor_type=reading_data.sensor_type,
        value=reading_data.value,
        unit=reading_data.unit
    )

    db.add(new_reading)
    db.commit()
    db.refresh(new_reading)

    return new_reading


# Отримання показників датчиків
@router.get("/readings", response_model=list[ReadingResponse])
def get_readings(
    device_code: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(SensorReading)

    if device_code:
        query = query.join(Device).filter(
            Device.device_code == device_code
        )

    return query.order_by(
        SensorReading.recorded_at.desc()
    ).limit(100).all()

# Створення правила автоматизації
@router.post("/rules", response_model=RuleResponse)
def create_rule(
    rule_data: RuleCreate,
    db: Session = Depends(get_db)
):
    allowed_operators = [
        "greater_than",
        "less_than",
        "equal",
        "greater_equal",
        "less_equal"
    ]

    if rule_data.operator not in allowed_operators:
        raise HTTPException(
            status_code=400,
            detail="Непідтримуваний оператор"
        )

    new_rule = AutomationRule(**rule_data.model_dump())

    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)

    return new_rule


# Отримання всіх правил
@router.get("/rules", response_model=list[RuleResponse])
def get_rules(db: Session = Depends(get_db)):
    return db.query(AutomationRule).all()


# Отримання журналу автоматичних подій
@router.get("/events", response_model=list[EventResponse])
def get_events(db: Session = Depends(get_db)):
    return db.query(AutomationEvent).order_by(
        AutomationEvent.created_at.desc()
    ).limit(100).all()
