
from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.utils.session import require_roles
from app.models.customer_profile import CustomerProfile

router = APIRouter(
    prefix="/customer",
    tags=["Customer Profile"]
)

templates = Jinja2Templates(directory="app/templates")


@router.get("/profile")
def customer_profile(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_roles("user"))
):
    profile = db.query(CustomerProfile).filter(
        CustomerProfile.user_id == user.id
    ).first()

    return templates.TemplateResponse(
        request=request,
        name="customer_profile.html",
        context={
            "user": user,
            "profile": profile
        }
    )


@router.post("/profile")
def save_customer_profile(
    phone: str = Form(...),
    address: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(require_roles("user"))
):
    profile = db.query(CustomerProfile).filter(
        CustomerProfile.user_id == user.id
    ).first()

    if profile:
        profile.phone = phone.strip()
        profile.address = address.strip()
    else:
        profile = CustomerProfile(
            user_id=user.id,
            phone=phone.strip(),
            address=address.strip()
        )
        db.add(profile)

    db.commit()

    return RedirectResponse(
        url="/customer/profile",
        status_code=303
    )
