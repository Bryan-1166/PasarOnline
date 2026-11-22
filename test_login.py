
from app.database import SessionLocal
from app.schemas.auth import UserLogin
from app.services.auth_service import login_user


db = SessionLocal()

try:
    data = UserLogin(
        email="contoh_user@gmail.com",
        password="PasswordContoh"
    )

    user = login_user(db, data)

    print("Login berhasil!")
    print("ID:", user.id)
    print("Nama:", user.full_name)
    print("Email:", user.email)
    print("Role:", user.role)

except ValueError as e:
    print("Login ditolak:", e)

except Exception as e:
    print("Error:", e)

finally:
    db.close()
