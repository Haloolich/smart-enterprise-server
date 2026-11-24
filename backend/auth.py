from pwdlib import PasswordHash


# Створення механізму хешування паролів
password_hasher = PasswordHash.recommended()


# Перетворення пароля на хеш
def hash_password(password: str) -> str:
    return password_hasher.hash(password)


# Перевірка пароля
def verify_password(
    password: str,
    hashed_password: str
) -> bool:
    return password_hasher.verify(
        password,
        hashed_password
    )