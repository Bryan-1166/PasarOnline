from sqlalchemy import (
    ForeignKey, String, DateTime, func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DeliveryPickup(Base):
    __tablename__ = "delivery_pickups"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    delivery_id: Mapped[int] = mapped_column(
        ForeignKey("deliveries.id", ondelete="CASCADE"),
        nullable=False
    )

    producer_id: Mapped[int | None] = mapped_column(
        ForeignKey("producers.id", ondelete="SET NULL"),
        nullable=True
    )

    # Snapshot informasi toko dan lokasi lapak
    producer_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    market_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    block: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    stall_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    floor: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="waiting",
        nullable=False
    )

    picked_up_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )