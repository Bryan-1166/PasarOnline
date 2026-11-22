from sqlalchemy import ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CartItem(Base):
    __tablename__ = "cart_items"

    __table_args__ = (
        UniqueConstraint(
            "cart_id",
            "product_unit_id",
            name="unique_cart_product_unit"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    cart_id: Mapped[int] = mapped_column(
        ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False
    )

    product_unit_id: Mapped[int] = mapped_column(
        ForeignKey("product_units.id"),
        nullable=False
    )

    quantity: Mapped[float] = mapped_column(
        Numeric(12, 3),
        default=1,
        nullable=False
    )