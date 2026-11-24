import sqlite3

connection = sqlite3.connect("smart_enterprise.db")

connection.execute(
    """
    UPDATE users
    SET role = ?, is_active = 1
    WHERE username = ?
    """,
    ("admin", "admin")
)

connection.commit()

result = connection.execute(
    "SELECT username, role, is_active FROM users WHERE username = ?",
    ("admin",)
).fetchone()

print("Дані адміністратора:", result)

connection.close()