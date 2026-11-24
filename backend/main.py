
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI

from backend.database.database import Base, engine
from backend.database import models
from backend.api.routes import router
from backend.mqtt_client import start_mqtt, stop_mqtt

from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.database.models import Actuator, DeviceCommand
from backend.logging_config import setup_logging
from backend.api.auth_routes import router as auth_router
from backend.api.user_routes import router as user_router

# Налаштування журналювання сервера
setup_logging()

# Створення таблиць бази даних
Base.metadata.create_all(bind=engine)


# Керування запуском і зупинкою сервера
@asynccontextmanager
async def lifespan(app: FastAPI):
    start_mqtt()

    yield

    stop_mqtt()


app = FastAPI(
    title="Smart Enterprise Infrastructure Server",
    description=(
        "Багатоканальний сервер інтелектуального "
        "керування інфраструктурою підприємства"
    ),
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(router)
app.include_router(auth_router)
app.include_router(user_router)

# Підключення статичних файлів
STATIC_DIR = Path(__file__).parent / "static"

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)


# Головна сторінка вебпанелі
@app.get("/dashboard", include_in_schema=False)
def dashboard():
    return FileResponse(STATIC_DIR / "dashboard.html")
# Сторінка авторизації
@app.get("/login", include_in_schema=False)
def login_page():
    return FileResponse(STATIC_DIR / "login.html")


@app.get("/")
def home():
    return {
        "system": "Smart Enterprise Infrastructure Server",
        "message": "Сервер успішно запущено!",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "server": "online",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/info")
def system_info():
    return {
        "name": "Smart Enterprise Infrastructure Server",
        "description": (
            "Система моніторингу та інтелектуального "
            "керування інфраструктурою підприємства"
        ),
        "technology": "Python + FastAPI + SQLAlchemy + MQTT",
        "database": "SQLite",
        "communication": "MQTT",
        "sensor_channels": 6,
        "physical_controller": "ESP32 (планується)"
    }
