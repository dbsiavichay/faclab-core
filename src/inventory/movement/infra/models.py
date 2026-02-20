from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.inventory.movement.domain.constants import MovementType
from src.shared.infra.database import Base


class MovementModel(Base):
    __tablename__ = "movements"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int]
    type: Mapped[MovementType]
    reason: Mapped[str | None] = mapped_column(String(128))
    date: Mapped[datetime | None] = mapped_column(default=datetime.now)
    created_at: Mapped[datetime | None] = mapped_column(default=datetime.now)
    product: Mapped["ProductModel"] = relationship(  # NOQA: F821
        back_populates="movements"
    )
