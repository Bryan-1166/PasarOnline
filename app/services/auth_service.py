
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.driver import Driver
from app.schemas.user import UserRegister
from app.schemas.auth import UserLogin
from app.utils.security import hash_password, verify_password


def register_user(db: Session, data: UserRegister):
    email = str(data.email).lower().strip()

    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:
        raise ValueError("Email sudah terdaftar")

    new_user = User(
        email=email,
        full_name=data.full_name.strip(),
        password_hash=hash_password(data.password),
        role=data.role
    )

    try:
        db.add(new_user)
        db.flush()

        # Buat profil driver secara otomatis
        if data.role == "driver":
            new_driver = Driver(
                user_id=new_user.id,
                phone=data.phone.strip(),
                status="standby"
            )

            db.add(new_driver)

        db.commit()
        db.refresh(new_user)

        return new_user

    except Exception:
        db.rollback()
        raise


def login_user(db: Session, data: UserLogin):
    email = str(data.email).lower().strip()

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        raise ValueError("Email atau password salah")

    if not verify_password(data.password, user.password_hash):
        raise ValueError("Email atau password salah")

    if not user.is_active:
        raise ValueError("Akun tidak aktif")

    return user
