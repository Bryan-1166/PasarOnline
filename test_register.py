
from app.database import SessionLocal
from app.schemas.user import UserRegister
from app.services.auth_service import register_user


db = SessionLocal()

try:
    data = UserRegister(
        email="contoh_user@gmail.com",
        full_name="Contoh Pengguna",
        password="PasswordContoh123!",
        confirm_password="PasswordContoh123!",
        role="user"
    )

    user = register_user(db, data)

    print("Registrasi berhasil!")
    print("ID:", user.id)
    print("Nama:", user.full_name)
    print("Email:", user.email)
    print("Role:", user.role)

except ValueError as e:
    print("Registrasi gagal:", e)

except Exception as e:
    print("Terjadi kesalahan:", e)

finally:
    db.close()
