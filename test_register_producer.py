
from app.database import SessionLocal
from app.schemas.user import UserRegister
from app.services.auth_service import register_user


db = SessionLocal()

try:
    data = UserRegister(
        email="contoh_producer@gmail.com",
        full_name="Contoh Penjual",
        password="PasswordProducer123!",
        confirm_password="PasswordProducer123!",
        role="producer"
    )

    user = register_user(db, data)

    print("Registrasi Producer berhasil!")
    print("ID:", user.id)
    print("Nama:", user.full_name)
    print("Email:", user.email)
    print("Role:", user.role)

except ValueError as e:
    print("Registrasi ditolak:", e)

except Exception as e:
    print("Error:", e)

finally:
    db.close()
