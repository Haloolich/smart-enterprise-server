
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database.database import get_db
from backend.database.models import User
from backend.dependencies import require_admin, get_current_user
from backend.auth import hash_password


router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
    dependencies=[Depends(require_admin)]
)


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=128)
    role: str = "user"


@router.get("/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id).all()

    return [
        {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at
        }
        for user in users
    ]


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    if user_data.role not in ["user", "admin"]:
        raise HTTPException(
            status_code=400,
            detail="Недопустима роль користувача"
        )

    existing_user = db.query(User).filter(
        User.username == user_data.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Користувач із таким логіном уже існує"
        )

    new_user = User(
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Користувача успішно створено",
        "id": new_user.id,
        "username": new_user.username,
        "role": new_user.role,
        "is_active": new_user.is_active
    }


class UserRoleUpdate(BaseModel):
    role: str


@router.patch("/{user_id}/role")
def update_user_role(
    user_id: int,
    user_data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user)
):
    if user_data.role not in ["user", "admin"]:
        raise HTTPException(
            status_code=400,
            detail="Недопустима роль користувача"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Користувача не знайдено"
        )

    if current_admin.id == user_id and user_data.role != "admin":
        raise HTTPException(
            status_code=400,
            detail="Не можна змінити власну роль адміністратора"
        )

    if (
        user.role == "admin"
        and user.is_active
        and user_data.role == "user"
    ):
        active_admins = db.query(User).filter(
            User.role == "admin",
            User.is_active == True
        ).count()

        if active_admins <= 1:
            raise HTTPException(
                status_code=400,
                detail="Не можна позбавити систему останнього активного адміністратора"
            )

    user.role = user_data.role
    db.commit()
    db.refresh(user)

    return {
        "message": "Роль користувача успішно змінено",
        "id": user.id,
        "username": user.username,
        "role": user.role
    }


class UserStatusUpdate(BaseModel):
    is_active: bool


@router.patch("/{user_id}/status")
def update_user_status(
    user_id: int,
    user_data: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Користувача не знайдено"
        )

    if current_admin.id == user_id and not user_data.is_active:
        raise HTTPException(
            status_code=400,
            detail="Не можна заблокувати власний обліковий запис"
        )

    if user.role == "admin" and not user_data.is_active:
        active_admins = db.query(User).filter(
            User.role == "admin",
            User.is_active == True
        ).count()

        if active_admins <= 1:
            raise HTTPException(
                status_code=400,
                detail="Не можна заблокувати останнього активного адміністратора"
            )

    user.is_active = user_data.is_active
    db.commit()
    db.refresh(user)

    return {
        "message": "Статус користувача успішно змінено",
        "id": user.id,
        "username": user.username,
        "is_active": user.is_active
    }

# Модель скидання пароля
class UserPasswordUpdate(BaseModel):
    password: str = Field(min_length=8, max_length=128)


# Скидання пароля користувача адміністратором
@router.patch("/{user_id}/password")
def update_user_password(
    user_id: int,
    user_data: UserPasswordUpdate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Користувача не знайдено"
        )

    user.password_hash = hash_password(user_data.password)

    db.commit()

    return {
        "message": "Пароль користувача успішно змінено",
        "id": user.id,
        "username": user.username
    }