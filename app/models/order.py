from sqlalchemy import (
    ForeignKey, String, Text, Numeric, DateTime, func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    order_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    # Total harga seluruh produk
    subtotal: Mapped[float] = mapped_column(
        Numeric(14, 2),
        nullable=False
    )

    # Biaya pengantaran sebesar 3% dari subtotal
    delivery_fee: Mapped[float] = mapped_column(
        Numeric(14, 2),
        nullable=False
    )

    # Subtotal + biaya pengantaran
    total_amount: Mapped[float] = mapped_column(
        Numeric(14, 2),
        nullable=False
    )

    # Alamat diisi setelah pembayaran dikonfirmasi
    delivery_address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="waiting_payment",
        nullable=False
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )