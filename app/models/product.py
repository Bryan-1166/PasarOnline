from sqlalchemy import String, Text, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    producer_id: Mapped[int] = mapped_column(
        ForeignKey("producers.id", ondelete="CASCADE"),
        nullable=False
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    image: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    # Satuan dasar stok, misalnya kg, liter, atau pcs
    base_unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    # Stok disimpan berdasarkan satuan dasar
    stock_quantity: Mapped[float] = mapped_column(
        Numeric(12, 3),
        default=0,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )