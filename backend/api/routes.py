
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.mqtt_client import send_manual_actuator_command
from backend.database.database import get_db
from backend.database.models import Device, SensorReading
from backend.api.schemas import (
    DeviceCreate,
    DeviceResponse,
    ReadingCreate,
    ReadingResponse,
    RuleCreate,
    RuleResponse,
    EventResponse,
    ControlModeUpdate,
    ControlModeResponse,
    ActuatorResponse,
    ActuatorCommandCreate,
    CommandHistoryResponse,
    RuleUpdate
)
from backend.database.models import (
    Device,
    SensorReading,
    AutomationRule,
    AutomationEvent,
    SystemSettings,
    Actuator,
    DeviceCommand
)
from backend.api.schemas import RuleCreate, RuleResponse, EventResponse
from backend.database.models import SystemSettings
from backend.api.schemas import ControlModeUpdate, ControlModeResponse
from backend.database.models import AuditLog

from backend.dependencies import get_current_user, require_admin
from backend.audit import log_action


router = APIRouter(
    prefix="/api",
    tags=["Database"],
    dependencies=[Depends(get_current_user)]
)


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
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
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

    # Запис дії до журналу аудиту
    log_action(
        db,
        action="create_rule",
        description=f"Створено правило автоматизації: {new_rule.name}",
        entity_type="rule",
        entity_id=new_rule.id
    )

    return new_rule



# Отримання всіх правил
@router.get("/rules", response_model=list[RuleResponse])
def get_rules(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    return db.query(AutomationRule).all()



# Редагування правила автоматизації
@router.put("/rules/{rule_id}", response_model=RuleResponse)
def update_rule(
    rule_id: int,
    rule_data: RuleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    rule = db.query(AutomationRule).filter(
        AutomationRule.id == rule_id
    ).first()

    if not rule:
        raise HTTPException(
            status_code=404,
            detail="Правило не знайдено"
        )

    allowed_operators = [
        "greater_than",
        "less_than",
        "equal",
        "greater_equal",
        "less_equal"
    ]

    update_data = rule_data.model_dump(exclude_unset=True)

    if (
        "operator" in update_data
        and update_data["operator"] not in allowed_operators
    ):
        raise HTTPException(
            status_code=400,
            detail="Непідтримуваний оператор"
        )

    for key, value in update_data.items():
        setattr(rule, key, value)

    db.commit()
    db.refresh(rule)

    # Запис редагування до журналу аудиту
    log_action(
        db,
        action="update_rule",
        description=(
            f"Відредаговано правило '{rule.name}'. "
            f"Змінені параметри: {', '.join(update_data.keys())}"
        ),
        entity_type="rule",
        entity_id=rule.id
    )

    return rule



# Видалення правила автоматизації
@router.delete("/rules/{rule_id}")
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    rule = db.query(AutomationRule).filter(
        AutomationRule.id == rule_id
    ).first()

    if not rule:
        raise HTTPException(
            status_code=404,
            detail="Правило не знайдено"
        )

    related_events = db.query(AutomationEvent).filter(
        AutomationEvent.rule_id == rule_id
    ).count()

    if related_events > 0:
        raise HTTPException(
            status_code=400,
            detail="Неможливо видалити правило, оскільки воно має історію виконання. Вимкніть його замість видалення."
        )

    # Зберігаємо назву до видалення об'єкта
    rule_name = rule.name

    db.delete(rule)
    db.commit()

    # Запис видалення до журналу аудиту
    log_action(
        db,
        action="delete_rule",
        description=f"Видалено правило автоматизації: {rule_name}",
        entity_type="rule",
        entity_id=rule_id
    )

    return {
        "message": "Правило успішно видалено"
    }



# Отримання журналу автоматичних подій
@router.get("/events", response_model=list[EventResponse])
def get_events(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    return db.query(AutomationEvent).order_by(
        AutomationEvent.created_at.desc()
    ).limit(100).all()


# Дозволені режими керування
ALLOWED_CONTROL_MODES = [
    "manual",
    "automatic",
    "mixed"
]


# Отримання або створення налаштувань системи
def get_or_create_settings(db: Session):
    settings = db.query(SystemSettings).filter(
        SystemSettings.id == 1
    ).first()

    if settings is None:
        settings = SystemSettings(
            id=1,
            control_mode="automatic"
        )

        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


# Отримання поточного режиму
@router.get(
    "/control/mode",
    response_model=ControlModeResponse
)
def get_control_mode(db: Session = Depends(get_db)):
    return get_or_create_settings(db)



# Зміна режиму керування
@router.put(
    "/control/mode",
    response_model=ControlModeResponse
)
def update_control_mode(
    mode_data: ControlModeUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    if mode_data.control_mode not in ALLOWED_CONTROL_MODES:
        raise HTTPException(
            status_code=400,
            detail="Невідомий режим керування"
        )

    settings = get_or_create_settings(db)

    # Зберігаємо попередній режим
    previous_mode = settings.control_mode

    settings.control_mode = mode_data.control_mode

    db.commit()
    db.refresh(settings)

    # Запис зміни режиму до журналу аудиту
    if previous_mode != settings.control_mode:
        log_action(
            db,
            action="change_control_mode",
            description=(
                f"Змінено режим керування: "
                f"{previous_mode} → {settings.control_mode}"
            ),
            entity_type="system_settings",
            entity_id=settings.id
        )

    return settings


# Отримання списку виконавчих пристроїв
@router.get("/actuators", response_model=list[ActuatorResponse])
def get_actuators(db: Session = Depends(get_db)):
    actuators = db.query(Actuator).order_by(Actuator.id).all()

    return actuators

# Ручне керування виконавчим пристроєм
@router.post("/actuators/{actuator_id}/command")
def control_actuator(
    actuator_id: int,
    data: ActuatorCommandCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    # Отримуємо поточний режим керування
    settings = get_or_create_settings(db)

    # В автоматичному режимі ручне керування заборонене
    if settings.control_mode == "automatic":
        raise HTTPException(
            status_code=403,
            detail="Ручне керування недоступне в автоматичному режимі"
        )

    # Знаходимо виконавчий пристрій
    actuator = db.query(Actuator).filter(
        Actuator.id == actuator_id
    ).first()

    if not actuator:
        raise HTTPException(
            status_code=404,
            detail="Виконавчий пристрій не знайдено"
        )

    # Сповіщення не підтримує команди увімкнення та вимкнення
    if actuator.actuator_type not in ["ventilation", "lighting"]:
        raise HTTPException(
            status_code=400,
            detail="Цей пристрій не підтримує ручне перемикання"
        )

    # Надсилаємо ручну команду
    result = send_manual_actuator_command(
        db,
        actuator,
        data.command
    )

    return {
        "message": "Команду оброблено",
        "actuator_code": actuator.code,
        "command": data.command,
        "state": actuator.state,
        "result": result
    }

# Отримання історії команд виконавчих пристроїв
@router.get(
    "/commands/history",
    response_model=list[CommandHistoryResponse]
)
def get_command_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    commands = (
        db.query(DeviceCommand)
        .join(Actuator)
        .order_by(DeviceCommand.created_at.desc())
        .limit(limit)
        .all()
    )

    history = []

    for command in commands:
        history.append({
            "id": command.id,
            "actuator_name": command.actuator.name,
            "actuator_code": command.actuator.code,
            "source": command.source,
            "command": command.command,
            "result": command.result,
            "created_at": command.created_at
        })

    return history

# Отримання журналу адміністративних дій
@router.get("/audit")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    return (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(100)
        .all()
    )