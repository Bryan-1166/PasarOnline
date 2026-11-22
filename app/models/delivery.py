from sqlalchemy import (
    ForeignKey, String, DateTime, Text, func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Delivery(Base):
    __tablename__ = "deliveries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    driver_id: Mapped[int | None] = mapped_column(
        ForeignKey("drivers.id", ondelete="SET NULL"),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="waiting_driver",
        nullable=False
    )

    # Waktu mulai dan batas pengambilan barang
    pickup_started_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    pickup_deadline_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Waktu mulai dan estimasi tiba di alamat customer
    travel_started_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    estimated_arrival_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    completed_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )