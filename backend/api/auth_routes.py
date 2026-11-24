from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import User
from backend.auth import hash_password, verify_password
from backend.token import create_access_token
from backend.dependencies import get_current_user


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


# Схема даних для реєстрації
class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=128)


# Схема даних для входу
class LoginRequest(BaseModel):
    username: str
    password: str


# Реєстрація користувача
@router.post("/register")
def register(
    credentials: RegisterRequest,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.username == credentials.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Користувач з таким логіном вже існує"
        )

    new_user = User(
        username=credentials.username,
        password_hash=hash_password(credentials.password),
        role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Користувача успішно зареєстровано",
        "username": new_user.username
    }


# Авторизація користувача
@router.post("/login")
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == credentials.username
    ).first()

    if not user or not verify_password(
        credentials.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Неправильний логін або пароль"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Обліковий запис деактивовано"
        )

    token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

# Отримання профілю авторизованого користувача
@router.get("/me")
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }