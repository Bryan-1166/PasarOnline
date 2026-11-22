from sqlalchemy import (
    ForeignKey, String, Numeric, DateTime, func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    payment_method: Mapped[str] = mapped_column(
        String(30),
        default="virtual_account",
        nullable=False
    )

    va_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    amount: Mapped[float] = mapped_column(
        Numeric(14, 2),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="waiting_confirmation",
        nullable=False
    )

    confirmed_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )