
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.auth import UserLogin
from app.schemas.user import UserRegister, UserResponse
from app.services.auth_service import login_user, register_user
from app.utils.session import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

templates = Jinja2Templates(directory="app/templates")


# =========================
# HALAMAN LOGIN
# =========================

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )


# =========================
# HALAMAN REGISTER
# =========================

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={}
    )


# =========================
# PROSES REGISTER
# =========================

@router.post("/register", response_model=UserResponse)
def register(
    data: UserRegister,
    db: Session = Depends(get_db)
):
    try:
        user = register_user(db, data)
        return user

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =========================
# PROSES LOGIN
# =========================

@router.post("/login")
def login(
    request: Request,
    data: UserLogin,
    db: Session = Depends(get_db)
):
    try:
        user = login_user(db, data)

        request.session.clear()
        request.session["user_id"] = user.id

        return {
            "message": "Login berhasil",
            "user": UserResponse.model_validate(user)
        }

    except ValueError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error)
        )


# =========================
# LOGOUT
# =========================

@router.post("/logout")
def logout(request: Request):
    request.session.clear()

    return {
        "message": "Logout berhasil"
    }


# =========================
# PROFIL USER LOGIN
# =========================

@router.get("/me", response_model=UserResponse)
def get_profile(
    request: Request,
    db: Session = Depends(get_db)
):
    return get_current_user(request, db)
