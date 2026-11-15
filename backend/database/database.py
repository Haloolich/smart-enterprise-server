
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# Визначаємо шлях до файлу бази даних
BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_PATH = BASE_DIR / "smart_enterprise.db"

# Створюємо адресу підключення до SQLite
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

# Створюємо підключення
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Створюємо фабрику сесій
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Базовий клас для моделей таблиць
class Base(DeclarativeBase):
    pass


# Функція для отримання сесії бази даних
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
