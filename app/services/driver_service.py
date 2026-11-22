
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from app.models.driver import Driver
from app.models.user import User
from app.models.delivery import Delivery
from app.models.delivery_pickup import DeliveryPickup
from app.models.order import Order


PICKUP_DURATION_MINUTES = 5
TRAVEL_DURATION_MINUTES = 15


# =========================
# PROFIL DRIVER
# =========================
def get_driver_profile(db: Session, user_id: int):
    return db.query(Driver).filter(
        Driver.user_id == user_id
    ).first()


# =========================
# PESANAN TERSEDIA
# =========================
def get_available_deliveries(db: Session):
    deliveries = db.query(Delivery).join(
        Order,
        Delivery.order_id == Order.id
    ).filter(
        Delivery.status == "ready_for_pickup",
        Order.status == "waiting_driver",
        Delivery.driver_id.is_(None)
    ).order_by(
        Delivery.created_at.asc()
    ).all()

    result = []

    for delivery in deliveries:

        pickups = db.query(DeliveryPickup).filter(
            DeliveryPickup.delivery_id == delivery.id
        ).order_by(DeliveryPickup.id.asc()).all()

        if not pickups:
            continue

        if not all(p.status == "ready" for p in pickups):
            continue

        order = db.query(Order).filter(
            Order.id == delivery.order_id
        ).first()

        if not order:
            continue

        customer = db.query(User).filter(
            User.id == order.user_id
        ).first()

        result.append({
            "delivery": delivery,
            "order": order,
            "customer": customer,
            "pickups": pickups
        })

    return result


# =========================
# PESANAN MILIK DRIVER
# =========================
def get_driver_deliveries(db: Session, user_id: int):
    driver = get_driver_profile(db, user_id)

    if not driver:
        raise ValueError("Profil driver tidak ditemukan")

    deliveries = db.query(Delivery).filter(
        Delivery.driver_id == driver.id
    ).order_by(
        Delivery.created_at.desc()
    ).all()

    result = []

    for delivery in deliveries:

        pickups = db.query(DeliveryPickup).filter(
            DeliveryPickup.delivery_id == delivery.id
        ).order_by(DeliveryPickup.id.asc()).all()

        active_pickup = next(
            (p for p in pickups if p.status == "in_progress"),
            None
        )

        next_pickup = next(
            (p for p in pickups if p.status == "ready"),
            None
        )

        order = db.query(Order).filter(
            Order.id == delivery.order_id
        ).first()

        customer = None

        if order:
            customer = db.query(User).filter(
                User.id == order.user_id
            ).first()

        result.append({
            "delivery": delivery,
            "order": order,
            "customer": customer,
            "pickups": pickups,
            "active_pickup": active_pickup,
            "next_pickup": next_pickup
        })

    return result


# =========================
# AMBIL PESANAN
# =========================
def take_delivery(db: Session, user_id: int, delivery_id: int):
    try:
        driver = db.query(Driver).filter(
            Driver.user_id == user_id
        ).with_for_update().first()

        if not driver:
            raise ValueError("Profil driver tidak ditemukan")

        if driver.status != "standby":
            raise ValueError("Driver sedang bertugas")

        delivery = db.query(Delivery).filter(
            Delivery.id == delivery_id
        ).with_for_update().first()

        if not delivery:
            raise ValueError("Pesanan tidak ditemukan")

        if delivery.driver_id is not None:
            raise ValueError("Pesanan sudah diambil driver lain")

        if delivery.status != "ready_for_pickup":
            raise ValueError("Pesanan belum siap diambil")

        order = db.query(Order).filter(
            Order.id == delivery.order_id
        ).first()

        if not order or order.status != "waiting_driver":
            raise ValueError(
                "Status pesanan tidak memungkinkan untuk diambil"
            )

        pickups = db.query(DeliveryPickup).filter(
            DeliveryPickup.delivery_id == delivery.id
        ).all()

        if not pickups:
            raise ValueError("Pesanan belum memiliki data pickup")

        if not all(p.status == "ready" for p in pickups):
            raise ValueError(
                "Belum semua producer menyiapkan barang"
            )

        delivery.driver_id = driver.id
        driver.status = "busy"

        db.commit()
        db.refresh(delivery)

        return delivery

    except Exception:
        db.rollback()
        raise


# =========================
# MULAI PICKUP
# =========================
def start_pickup(db: Session, user_id: int, delivery_id: int):
    try:
        driver = db.query(Driver).filter(
            Driver.user_id == user_id
        ).with_for_update().first()

        if not driver:
            raise ValueError("Profil driver tidak ditemukan")

        delivery = db.query(Delivery).filter(
            Delivery.id == delivery_id,
            Delivery.driver_id == driver.id
        ).with_for_update().first()

        if not delivery:
            raise ValueError(
                "Pesanan tidak ditemukan atau bukan milik Anda"
            )

        if delivery.status not in ["ready_for_pickup", "picking_up"]:
            raise ValueError(
                "Pesanan tidak sedang dalam tahap pickup"
            )

        pickups = db.query(DeliveryPickup).filter(
            DeliveryPickup.delivery_id == delivery.id
        ).order_by(
            DeliveryPickup.id.asc()
        ).with_for_update().all()

        if not pickups:
            raise ValueError("Tidak ada lokasi pickup")

        if any(p.status == "in_progress" for p in pickups):
            raise ValueError("Pickup sedang berlangsung")

        pickup = next(
            (p for p in pickups if p.status == "ready"),
            None
        )

        if not pickup:
            raise ValueError(
                "Semua barang sudah selesai diambil"
            )

        now = datetime.now(timezone.utc)

        pickup.status = "in_progress"
        delivery.status = "picking_up"
        delivery.pickup_started_at = now
        delivery.pickup_deadline_at = (
            now + timedelta(minutes=PICKUP_DURATION_MINUTES)
        )

        db.commit()
        db.refresh(delivery)
        db.refresh(pickup)

        return pickup

    except Exception:
        db.rollback()
        raise


# =========================
# SELESAIKAN PICKUP
# =========================
def complete_pickup(db: Session, user_id: int, delivery_id: int):
    try:
        driver = db.query(Driver).filter(
            Driver.user_id == user_id
        ).with_for_update().first()

        if not driver:
            raise ValueError("Profil driver tidak ditemukan")

        delivery = db.query(Delivery).filter(
            Delivery.id == delivery_id,
            Delivery.driver_id == driver.id
        ).with_for_update().first()

        if not delivery:
            raise ValueError(
                "Pesanan tidak ditemukan atau bukan milik Anda"
            )

        if delivery.status != "picking_up":
            raise ValueError(
                "Pesanan tidak sedang dalam proses pickup"
            )

        pickups = db.query(DeliveryPickup).filter(
            DeliveryPickup.delivery_id == delivery.id
        ).order_by(
            DeliveryPickup.id.asc()
        ).with_for_update().all()

        active_pickup = next(
            (p for p in pickups if p.status == "in_progress"),
            None
        )

        if not active_pickup:
            raise ValueError(
                "Tidak ada pickup yang sedang berlangsung"
            )

        now = datetime.now(timezone.utc)

        active_pickup.status = "picked_up"
        active_pickup.picked_up_at = now

        delivery.pickup_started_at = None
        delivery.pickup_deadline_at = None

        all_completed = all(
            p.status == "picked_up"
            for p in pickups
        )

        if all_completed:
            delivery.status = "pickup_completed"
        else:
            delivery.status = "ready_for_pickup"

        db.commit()
        db.refresh(delivery)

        return delivery

    except Exception:
        db.rollback()
        raise


# =========================
# MULAI PERJALANAN
# =========================
def start_travel(db: Session, user_id: int, delivery_id: int):
    try:
        driver = db.query(Driver).filter(
            Driver.user_id == user_id
        ).with_for_update().first()

        if not driver:
            raise ValueError("Profil driver tidak ditemukan")

        delivery = db.query(Delivery).filter(
            Delivery.id == delivery_id,
            Delivery.driver_id == driver.id
        ).with_for_update().first()

        if not delivery:
            raise ValueError(
                "Pesanan tidak ditemukan atau bukan milik Anda"
            )

        if delivery.status != "pickup_completed":
            raise ValueError(
                "Semua pickup harus selesai sebelum perjalanan dimulai"
            )

        order = db.query(Order).filter(
            Order.id == delivery.order_id
        ).first()

        if not order:
            raise ValueError("Data pesanan tidak ditemukan")

        now = datetime.now(timezone.utc)

        delivery.status = "in_transit"
        delivery.travel_started_at = now
        delivery.estimated_arrival_at = (
            now + timedelta(minutes=TRAVEL_DURATION_MINUTES)
        )

        db.commit()
        db.refresh(delivery)

        return delivery

    except Exception:
        db.rollback()
        raise


# =========================
# SELESAIKAN PENGANTARAN
# =========================
def complete_delivery(db: Session, user_id: int, delivery_id: int):
    try:
        driver = db.query(Driver).filter(
            Driver.user_id == user_id
        ).with_for_update().first()

        if not driver:
            raise ValueError("Profil driver tidak ditemukan")

        delivery = db.query(Delivery).filter(
            Delivery.id == delivery_id,
            Delivery.driver_id == driver.id
        ).with_for_update().first()

        if not delivery:
            raise ValueError(
                "Pesanan tidak ditemukan atau bukan milik Anda"
            )

        if delivery.status != "in_transit":
            raise ValueError(
                "Pesanan belum dalam perjalanan"
            )

        order = db.query(Order).filter(
            Order.id == delivery.order_id
        ).with_for_update().first()

        if not order:
            raise ValueError("Data pesanan tidak ditemukan")

        now = datetime.now(timezone.utc)

        delivery.status = "completed"
        delivery.completed_at = now

        order.status = "delivered"

        driver.status = "standby"

        db.commit()

        db.refresh(delivery)
        db.refresh(order)
        db.refresh(driver)

        return delivery

    except Exception:
        db.rollback()
        raise
