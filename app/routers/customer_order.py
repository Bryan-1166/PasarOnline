
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.utils.session import require_roles

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.delivery import Delivery
from app.models.delivery_pickup import DeliveryPickup
from app.models.order_status_history import OrderStatusHistory
from app.models.product_review import ProductReview


router = APIRouter(
    prefix="/customer/orders",
    tags=["Customer Orders"]
)

templates = Jinja2Templates(directory="app/templates")


# ==========================================
# DAFTAR RIWAYAT PESANAN CUSTOMER
# ==========================================

@router.get("/")
def customer_orders(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_roles("user"))
):
    orders = (
        db.query(Order)
        .filter(Order.user_id == user.id)
        .order_by(Order.created_at.desc())
        .all()
    )

    order_data = []

    for order in orders:
        payment = db.query(Payment).filter(
            Payment.order_id == order.id
        ).first()

        delivery = db.query(Delivery).filter(
            Delivery.order_id == order.id
        ).first()

        item_count = db.query(OrderItem).filter(
            OrderItem.order_id == order.id
        ).count()

        order_data.append({
            "order": order,
            "payment": payment,
            "delivery": delivery,
            "item_count": item_count
        })

    return templates.TemplateResponse(
        request=request,
        name="customer_orders.html",
        context={
            "user": user,
            "orders": order_data
        }
    )


# ==========================================
# DETAIL SATU PESANAN CUSTOMER
# ==========================================

@router.get("/{order_id}")
def customer_order_detail(
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

    order_items = db.query(OrderItem).filter(
        OrderItem.order_id == order.id
    ).all()

    delivery = db.query(Delivery).filter(
        Delivery.order_id == order.id
    ).first()

    pickups = []

    if delivery:
        pickups = (
            db.query(DeliveryPickup)
            .filter(DeliveryPickup.delivery_id == delivery.id)
            .order_by(DeliveryPickup.id.asc())
            .all()
        )

    status_history = (
        db.query(OrderStatusHistory)
        .filter(OrderStatusHistory.order_id == order.id)
        .order_by(OrderStatusHistory.created_at.asc())
        .all()
    )

    # Ambil review yang sudah dibuat untuk setiap item
    reviews = {}

    for item in order_items:
        review = db.query(ProductReview).filter(
            ProductReview.order_item_id == item.id
        ).first()

        reviews[item.id] = review

    return templates.TemplateResponse(
        request=request,
        name="customer_order_detail.html",
        context={
            "user": user,
            "order": order,
            "payment": payment,
            "order_items": order_items,
            "delivery": delivery,
            "pickups": pickups,
            "status_history": status_history,
            "reviews": reviews
        }
    )


# ==========================================
# CUSTOMER MEMBERIKAN RATING DAN ULASAN
# ==========================================

@router.post("/{order_id}/review/{order_item_id}")
def create_product_review(
    order_id: int,
    order_item_id: int,
    rating: int = Form(...),
    review: str = Form(""),
    db: Session = Depends(get_db),
    user=Depends(require_roles("user"))
):
    # Validasi rating
    if rating < 1 or rating > 5:
        raise HTTPException(
            status_code=400,
            detail="Rating harus antara 1 sampai 5"
        )

    # Pastikan pesanan milik customer dan sudah selesai
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user.id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Pesanan tidak ditemukan"
        )

    if order.status != "delivered":
        raise HTTPException(
            status_code=400,
            detail="Ulasan hanya dapat diberikan setelah pesanan diterima"
        )

    # Pastikan item benar-benar bagian dari pesanan tersebut
    order_item = db.query(OrderItem).filter(
        OrderItem.id == order_item_id,
        OrderItem.order_id == order.id
    ).first()

    if not order_item or order_item.product_id is None:
        raise HTTPException(
            status_code=404,
            detail="Item pesanan tidak ditemukan"
        )

    # Cek apakah item sudah pernah diberi review
    existing_review = db.query(ProductReview).filter(
        ProductReview.order_item_id == order_item.id
    ).first()

    if existing_review:
        raise HTTPException(
            status_code=400,
            detail="Item ini sudah pernah diberi ulasan"
        )

    new_review = ProductReview(
        product_id=order_item.product_id,
        user_id=user.id,
        order_item_id=order_item.id,
        rating=rating,
        review=review.strip() or None
    )

    db.add(new_review)
    db.commit()

    return RedirectResponse(
        url=f"/customer/orders/{order_id}",
        status_code=303
    )
