
from app.database import SessionLocal
from app.schemas.user import UserRegister
from app.services.auth_service import register_user

db = SessionLocal()

try:
    data = UserRegister(
        email="contoh_user@gmail.com",
        full_name="Pengguna Kedua",
        password="PasswordContoh123!",
        confirm_password="PasswordContoh123!",
        role="user"
    )

    user = register_user(db, data)

    print("Registrasi berhasil:", user.email)

except ValueError as e:
    print("Validasi berhasil:", e)

except Exception as e:
    print("Error:", e)

finally:
    db.close()
