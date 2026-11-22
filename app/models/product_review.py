
from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    DateTime,
    Integer,
    CheckConstraint,
    UniqueConstraint,
    func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ProductReview(Base):
    __tablename__ = "product_reviews"

    __table_args__ = (
        CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="check_product_review_rating"
        ),
        UniqueConstraint(
            "order_item_id",
            name="unique_product_review_order_item"
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    order_item_id: Mapped[int] = mapped_column(
        ForeignKey("order_items.id", ondelete="CASCADE"),
        nullable=False
    )

    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    review: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
