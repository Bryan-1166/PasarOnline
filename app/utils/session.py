
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.models.user import User
from app.dependencies import get_db


def get_current_user(request: Request, db: Session):
    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Silakan login terlebih dahulu"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active:
        request.session.clear()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesi tidak valid atau akun tidak aktif"
        )

    return user


def require_roles(*allowed_roles):

    def role_checker(
        request: Request,
        db: Session = Depends(get_db)
    ):
        user = get_current_user(request, db)

        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Anda tidak memiliki akses ke halaman ini"
            )

        return user

    return role_checker
