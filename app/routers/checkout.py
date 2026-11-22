
import logging
from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request,
    Form
)
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.utils.session import require_roles
from app.services.checkout_service import create_checkout

from app.models.order import Order
from app.models.payment import Payment
from app.models.order_item import OrderItem
from app.models.delivery import Delivery
from app.models.delivery_pickup import DeliveryPickup
from app.models.producer import Producer
from app.models.order_status_history import OrderStatusHistory


router = APIRouter(
    prefix="/customer/checkout",
    tags=["Customer Checkout"]
)

templates = Jinja2Templates(directory="app/templates")


# ==========================================
# PROSES CHECKOUT
# ==========================================

@router.post("/", status_code=status.HTTP_201_CREATED)
def checkout(
    db: Session = Depends(get_db),
    user=Depends(require_roles("user"))
):
    try:
        return create_checkout(db, user)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception:
        db.rollback()
        logging.exception("ERROR SAAT PROSES CHECKOUT")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan saat memproses checkout"
        )


# ==========================================
# HALAMAN PEMBAYARAN
# ==========================================

@router.get("/payment/{order_id}")
def payment_page(
    order_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_roles("user"))
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user.id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Pesanan tidak ditemukan"
        )

    payment = db.query(Payment).filter(
        Payment.order_id == order.id
    ).first()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Data pembayaran tidak ditemukan"
        )

    order_items = db.query(OrderItem).filter(
        OrderItem.order_id == order.id
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="customer_payment.html",
        context={
            "user": user,
            "order": order,
            "payment": payment,
            "order_items": order_items
        }
    )


# ==========================================
# KONFIRMASI PEMBAYARAN + CATATAN OPSIONAL
# ==========================================

@router.post("/payment/{order_id}/confirm")
def confirm_payment(
    order_id: int,
    delivery_note: str = Form(default=""),
    db: Session = Depends(get_db),
    user=Depends(require_roles("user"))
):
    try:
        # Cari dan kunci pesanan
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == user.id
        ).with_for_update().first()

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Pesanan tidak ditemukan"
            )

        # Cari dan kunci pembayaran
        payment = db.query(Payment).filter(
            Payment.order_id == order.id
        ).with_for_update().first()

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Pembayaran tidak ditemukan"
            )

        # Validasi status pesanan
        if order.status != "waiting_payment":
            raise HTTPException(
                status_code=400,
                detail="Pesanan tidak dapat dikonfirmasi"
            )

        if payment.status != "waiting_confirmation":
            raise HTTPException(
                status_code=400,
                detail="Status pembayaran tidak valid"
            )

        # Validasi catatan pengiriman
        note = delivery_note.strip()

        if len(note) > 1000:
            raise HTTPException(
                status_code=400,
                detail="Catatan maksimal 1000 karakter"
            )

        # ==========================================
        # KONFIRMASI PEMBAYARAN
        # ==========================================

        payment.status = "confirmed"
        payment.confirmed_at = datetime.now(timezone.utc)

        # Simpan catatan opsional
        order.delivery_address = note or None

        # Ubah status pesanan
        order.status = "waiting_driver"

        # ==========================================
        # BUAT DATA DELIVERY
        # ==========================================

        delivery = db.query(Delivery).filter(
            Delivery.order_id == order.id
        ).with_for_update().first()

        if not delivery:
            delivery = Delivery(
                order_id=order.id,
                status="waiting_driver"
            )

            db.add(delivery)

            # Pastikan delivery.id sudah tersedia
            db.flush()

        # ==========================================
        # BUAT DATA PICKUP UNTUK SETIAP PRODUSEN
        # ==========================================

        existing_pickups = db.query(DeliveryPickup).filter(
            DeliveryPickup.delivery_id == delivery.id
        ).count()

        # Cegah pembuatan pickup duplikat
        if existing_pickups == 0:

            order_items = db.query(OrderItem).filter(
                OrderItem.order_id == order.id
            ).all()

            # Ambil ID produsen yang unik
            producer_ids = list({
                item.producer_id
                for item in order_items
                if item.producer_id is not None
            })

            for producer_id in producer_ids:

                producer = db.query(Producer).filter(
                    Producer.id == producer_id
                ).first()

                # Ambil salah satu item sebagai sumber
                # nama produsen cadangan
                producer_item = next(
                    (
                        item for item in order_items
                        if item.producer_id == producer_id
                    ),
                    None
                )

                if not producer_item:
                    continue

                pickup = DeliveryPickup(
                    delivery_id=delivery.id,
                    producer_id=producer_id,

                    producer_name=(
                        producer.shop_name
                        if producer and producer.shop_name
                        else producer_item.producer_name
                    ),

                    market_name=(
                        producer.market_name
                        if producer and producer.market_name
                        else "-"
                    ),

                    block=(
                        producer.block
                        if producer and producer.block
                        else "-"
                    ),

                    stall_number=(
                        producer.stall_number
                        if producer and producer.stall_number
                        else "-"
                    ),

                    floor=(
                        producer.floor
                        if producer and producer.floor
                        else "-"
                    ),

                    status="waiting"
                )

                db.add(pickup)

        # ==========================================
        # SIMPAN RIWAYAT STATUS
        # ==========================================

        history = OrderStatusHistory(
            order_id=order.id,
            status="waiting_driver",
            description=(
                "Pembayaran dikonfirmasi (simulasi). "
                "Pesanan menunggu driver."
            ),
            changed_by=user.id
        )

        db.add(history)

        # ==========================================
        # SIMPAN SELURUH PERUBAHAN
        # ==========================================

        db.commit()

        return RedirectResponse(
            url=f"/customer/checkout/payment/{order.id}",
            status_code=303
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()

        logging.exception(
            "ERROR SAAT KONFIRMASI PEMBAYARAN ORDER ID %s",
            order_id
        )

        raise HTTPException(
            status_code=500,
            detail="Gagal mengonfirmasi pembayaran"
        )
