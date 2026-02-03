from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.inventory.movement.domain.constants import MovementType
from src.shared.infra.db import Base


class MovementModel(Base):
    __tablename__ = "movements"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int]
    type: Mapped[MovementType]
    reason: Mapped[Optional[str]] = mapped_column(String(128))
    date: Mapped[Optional[datetime]] = mapped_column(default=datetime.now)
    created_at: Mapped[Optional[datetime]] = mapped_column(default=datetime.now)
    product: Mapped["ProductModel"] = relationship(  # NOQA: F821
        back_populates="movements"
    )
