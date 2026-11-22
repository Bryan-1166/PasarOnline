from sqlalchemy import String, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ProductUnit(Base):
    __tablename__ = "product_units"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )

    unit_name: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    # Konversi ke satuan dasar produk
    conversion_factor: Mapped[float] = mapped_column(
        Numeric(12, 3),
        nullable=False
    )

    # Harga untuk satu pilihan satuan
    price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )