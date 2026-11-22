
from sqlalchemy.orm import Session

from app.models.producer import Producer
from app.models.user import User
from app.models.delivery_pickup import DeliveryPickup
from app.models.delivery import Delivery
from app.models.order import Order
from app.models.order_item import OrderItem
from app.schemas.producer import ProducerProfileCreate


# ==========================================
# PRODUCER PROFILE
# ==========================================

def create_producer_profile(
    db: Session,
    user: User,
    data: ProducerProfileCreate
):
    if user.role != "producer":
        raise ValueError("Akun ini bukan akun penjual")

    existing_profile = db.query(Producer).filter(
        Producer.user_id == user.id
    ).first()

    if existing_profile:
        raise ValueError("Profil toko sudah dibuat")

    new_profile = Producer(
        user_id=user.id,
        shop_name=data.shop_name.strip(),
        phone=data.phone.strip(),
        description=data.description,
        market_name=data.market_name.strip(),
        block=data.block,
        stall_number=data.stall_number.strip(),
        floor=data.floor
    )

    try:
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
        return new_profile
    except Exception:
        db.rollback()
        raise


def get_producer_profile(db: Session, user_id: int):
    return db.query(Producer).filter(
        Producer.user_id == user_id
    ).first()


def update_producer_profile(
    db: Session,
    user_id: int,
    data: ProducerProfileCreate
):
    profile = get_producer_profile(db, user_id)

    if not profile:
        raise ValueError("Profil toko belum dibuat")

    profile.shop_name = data.shop_name.strip()
    profile.phone = data.phone.strip()
    profile.description = data.description
    profile.market_name = data.market_name.strip()
    profile.block = data.block
    profile.stall_number = data.stall_number.strip()
    profile.floor = data.floor

    try:
        db.commit()
        db.refresh(profile)
        return profile
    except Exception:
        db.rollback()
        raise


# ==========================================
# PRODUCER ORDER MANAGEMENT
# ==========================================

def get_producer_orders(db: Session, user_id: int):

    producer = get_producer_profile(db, user_id)

    if not producer:
        raise ValueError("Profil toko belum dibuat")

    pickups = (
        db.query(DeliveryPickup, Delivery, Order)
        .join(
            Delivery,
            DeliveryPickup.delivery_id == Delivery.id
        )
        .join(
            Order,
            Delivery.order_id == Order.id
        )
        .filter(
            DeliveryPickup.producer_id == producer.id
        )
        .order_by(
            Order.created_at.desc(),
            DeliveryPickup.id.desc()
        )
        .all()
    )

    result = []

    for pickup, delivery, order in pickups:

        items = (
            db.query(OrderItem)
            .filter(
                OrderItem.order_id == order.id,
                OrderItem.producer_id == producer.id
            )
            .order_by(OrderItem.id.asc())
            .all()
        )

        result.append({
            "pickup": pickup,
            "delivery": delivery,
            "order": order,
            "items": items
        })

    return result


# ==========================================
# MARK ORDER AS READY
# ==========================================

def mark_pickup_ready(
    db: Session,
    user_id: int,
    pickup_id: int
):

    producer = get_producer_profile(db, user_id)

    if not producer:
        raise ValueError("Profil toko belum dibuat")

    pickup = (
        db.query(DeliveryPickup)
        .filter(
            DeliveryPickup.id == pickup_id,
            DeliveryPickup.producer_id == producer.id
        )
        .with_for_update()
        .first()
    )

    if not pickup:
        raise ValueError("Pesanan toko tidak ditemukan")

    if pickup.status == "picked_up":
        raise ValueError("Pesanan sudah diambil driver")

    if pickup.status == "ready":
        return pickup

    if pickup.status != "waiting":
        raise ValueError("Status pickup tidak valid")

    delivery = (
        db.query(Delivery)
        .filter(Delivery.id == pickup.delivery_id)
        .with_for_update()
        .first()
    )

    if not delivery:
        raise ValueError("Data delivery tidak ditemukan")

    if delivery.status in ("completed", "cancelled", "canceled"):
        raise ValueError("Pesanan sudah selesai atau dibatalkan")

    try:
        pickup.status = "ready"

        all_pickups = db.query(DeliveryPickup).filter(
            DeliveryPickup.delivery_id == delivery.id
        ).all()

        if all_pickups and all(
            item.status in ("ready", "picked_up")
            for item in all_pickups
        ):
            delivery.status = "ready_for_pickup"

        db.commit()
        db.refresh(pickup)

        return pickup

    except Exception:
        db.rollback()
        raise
