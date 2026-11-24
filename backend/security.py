import os

from dotenv import load_dotenv
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader


# Завантаження змінних із .env
load_dotenv()

# Отримання секретного ключа
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise RuntimeError(
        "API_KEY не знайдено у файлі .env"
    )


# Заголовок для передавання ключа
api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)


# Перевірка ключа доступу
def verify_api_key(
    api_key: str = Security(api_key_header)
):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Недійсний або відсутній API-ключ"
        )

    return api_key