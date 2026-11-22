from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Producer(Base):
    __tablename__ = "producers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    shop_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    shop_photo: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    market_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    block: Mapped[str | None] = mapped_column(String(50), nullable=True)

    stall_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    floor: Mapped[str | None] = mapped_column(String(50), nullable=True)