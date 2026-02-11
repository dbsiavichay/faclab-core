from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.infra.db import Base


class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str | None] = mapped_column(String(128))

    products: Mapped[list["ProductModel"]] = relationship(back_populates="category")


class ProductModel(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    sku: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=True)
    category: Mapped[Optional["CategoryModel"]] = relationship(
        back_populates="products"
    )
    movements: Mapped[list["MovementModel"]] = relationship(  # NOQA: F821
        back_populates="product", cascade="all, delete-orphan"
    )
    stocks: Mapped[list["StockModel"]] = relationship(  # NOQA: F821
        back_populates="product", cascade="all, delete-orphan"
    )
