
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.utils.session import require_roles
from app.services.driver_service import (
    get_driver_profile,
    get_available_deliveries,
    get_driver_deliveries,
    take_delivery,
    start_pickup,
    complete_pickup,
    start_travel,
    complete_delivery
)

router = APIRouter(
    prefix="/driver",
    tags=["Driver"]
)

templates = Jinja2Templates(directory="app/templates")


# =========================
# DASHBOARD DRIVER
# =========================
@router.get("/dashboard")
def driver_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_roles("driver"))
):
    driver = get_driver_profile(db, user.id)

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Profil driver tidak ditemukan"
        )

    available_deliveries = get_available_deliveries(db)

    my_deliveries = get_driver_deliveries(
        db,
        user.id
    )

    return templates.TemplateResponse(
        request=request,
        name="driver_dashboard.html",
        context={
            "user": user,
            "driver": driver,
            "available_deliveries": available_deliveries,
            "my_deliveries": my_deliveries
        }
    )


# =========================
# PROFIL DRIVER
# =========================
@router.get("/profile")
def driver_profile(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_roles("driver"))
):
    driver = get_driver_profile(db, user.id)

    if not driver:
        raise HTTPException(
            status_code=404,
            detail="Profil driver tidak ditemukan"
        )

    return templates.TemplateResponse(
        request=request,
        name="driver_profile.html",
        context={
            "user": user,
            "driver": driver
        }
    )


# =========================
# AMBIL PESANAN
# =========================
@router.post("/deliveries/{delivery_id}/take")
def driver_take_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("driver"))
):
    try:
        take_delivery(db, user.id, delivery_id)

        return RedirectResponse(
            url="/driver/dashboard",
            status_code=303
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


# =========================
# MULAI PICKUP
# =========================
@router.post("/deliveries/{delivery_id}/start-pickup")
def driver_start_pickup(
    delivery_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("driver"))
):
    try:
        start_pickup(db, user.id, delivery_id)

        return RedirectResponse(
            url="/driver/dashboard",
            status_code=303
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


# =========================
# SELESAIKAN PICKUP
# =========================
@router.post("/deliveries/{delivery_id}/complete-pickup")
def driver_complete_pickup(
    delivery_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("driver"))
):
    try:
        complete_pickup(db, user.id, delivery_id)

        return RedirectResponse(
            url="/driver/dashboard",
            status_code=303
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


# =========================
# MULAI PERJALANAN
# =========================
@router.post("/deliveries/{delivery_id}/start-travel")
def driver_start_travel(
    delivery_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("driver"))
):
    try:
        start_travel(db, user.id, delivery_id)

        return RedirectResponse(
            url="/driver/dashboard",
            status_code=303
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


# =========================
# SELESAIKAN PENGANTARAN
# =========================
@router.post("/deliveries/{delivery_id}/complete")
def driver_complete_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("driver"))
):
    try:
        complete_delivery(db, user.id, delivery_id)

        return RedirectResponse(
            url="/driver/dashboard",
            status_code=303
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
