
import logging
import os
from logging.handlers import RotatingFileHandler


# Папка для журналів
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "server.log")


def setup_logging():

    # Формат повідомлень
    log_format = (
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    )

    formatter = logging.Formatter(log_format)

    # Запис у файл з обмеженням розміру
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )

    file_handler.setFormatter(formatter)

    # Виведення в консоль
    console_handler = logging.StreamHandler()

    console_handler.setFormatter(formatter)

    # Налаштування кореневого журналу
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            file_handler,
            console_handler
        ],
        force=True
    )
