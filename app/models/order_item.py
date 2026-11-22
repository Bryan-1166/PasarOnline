from sqlalchemy import (
    ForeignKey, String, Numeric
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )

    # Referensi produk asli, boleh kosong jika produk dihapus
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True
    )

    product_unit_id: Mapped[int | None] = mapped_column(
        ForeignKey("product_units.id", ondelete="SET NULL"),
        nullable=True
    )

    producer_id: Mapped[int | None] = mapped_column(
        ForeignKey("producers.id", ondelete="SET NULL"),
        nullable=True
    )

    # Snapshot informasi saat transaksi
    product_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    producer_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    unit_name: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    quantity: Mapped[float] = mapped_column(
        Numeric(12, 3),
        nullable=False
    )

    unit_price: Mapped[float] = mapped_column(
        Numeric(14, 2),
        nullable=False
    )

    subtotal: Mapped[float] = mapped_column(
        Numeric(14, 2),
        nullable=False
    )