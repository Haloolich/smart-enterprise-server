
import sys
import json
import urllib.request
import urllib.error
import importlib.util
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SERVER_URL = "http://127.0.0.1:8000"

errors = 0
passed = 0


def check(condition, message):
    global errors, passed

    if condition:
        print("[OK] " + message)
        passed += 1
    else:
        print("[ERROR] " + message)
        errors += 1


def request(endpoint):
    url = SERVER_URL + endpoint

    try:
        req = urllib.request.Request(
            url,
            headers={"Accept": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=5) as response:
            body = response.read().decode("utf-8")

            return response.status, body

    except (urllib.error.URLError, TimeoutError) as error:
        print("[ERROR] Запит " + endpoint + ": " + str(error))
        return None, None


print("=" * 60)
print("SMART ENTERPRISE INFRASTRUCTURE SERVER")
print("КОМПЛЕКСНЕ ТЕСТУВАННЯ")
print("=" * 60)


# 1. Python
print("\n1. Перевірка середовища")

check(
    sys.version_info >= (3, 10),
    "Версія Python не нижча за 3.10"
)


# 2. Структура проєкту
print("\n2. Перевірка файлів")

required_files = [
    "backend/__init__.py",
    "backend/main.py",
    "requirements.txt"
]

for filename in required_files:
    check(
        (BASE_DIR / filename).is_file(),
        "Знайдено " + filename
    )


# 3. Залежності
print("\n3. Перевірка бібліотек")

for package in ["fastapi", "uvicorn"]:
    check(
        importlib.util.find_spec(package) is not None,
        "Встановлена бібліотека " + package
    )


# 4. Перевірка головної сторінки
print("\n4. Перевірка API")

status, body = request("/")

home = None

if status == 200:
    try:
        home = json.loads(body)
    except json.JSONDecodeError:
        pass

check(
    home is not None
    and home.get("status") == "running",
    "Головна сторінка API працює"
)


# 5. Перевірка стану сервера
status, body = request("/api/health")

health = None

if status == 200:
    try:
        health = json.loads(body)
    except json.JSONDecodeError:
        pass

check(
    health is not None
    and health.get("status") == "healthy"
    and health.get("server") == "online",
    "Перевірка працездатності сервера успішна"
)


# 6. Перевірка інформації
status, body = request("/api/info")

info = None

if status == 200:
    try:
        info = json.loads(body)
    except json.JSONDecodeError:
        pass

check(
    info is not None
    and info.get("sensor_channels") == 6,
    "Система містить інформацію про шість каналів"
)


# 7. Перевірка OpenAPI
print("\n5. Перевірка документації API")

status, body = request("/openapi.json")

schema = None

if status == 200:
    try:
        schema = json.loads(body)
    except json.JSONDecodeError:
        pass

check(
    schema is not None,
    "OpenAPI-схема доступна"
)

if schema is not None:
    paths = schema.get("paths", {})

    required_routes = [
        "/",
        "/api/health",
        "/api/info"
    ]

    for route in required_routes:
        check(
            route in paths,
            "Маршрут зареєстрований: " + route
        )


# 8. Перевірка Swagger UI
status, body = request("/docs")

check(
    status == 200
    and body is not None
    and "swagger" in body.lower(),
    "Документація Swagger доступна"
)


# 9. Підсумок
print("\n" + "=" * 60)
print("РЕЗУЛЬТАТИ ТЕСТУВАННЯ")
print("=" * 60)

print("Успішних перевірок:", passed)
print("Помилок:", errors)

if errors == 0:
    print("\nУСІ ПЕРЕВІРКИ ПРОЙДЕНО!")
    print("Серверна частина готова до наступного етапу.")
else:
    print("\nВИЯВЛЕНО ПОМИЛКИ!")
    print("Необхідно виправити проблеми перед продовженням.")

print("=" * 60)
