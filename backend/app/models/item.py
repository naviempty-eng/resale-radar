from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    brand: Mapped[str] = mapped_column(String(120), index=True)
    country: Mapped[str] = mapped_column(String(40), index=True)
    platform: Mapped[str] = mapped_column(String(80), index=True)
    category: Mapped[str] = mapped_column(String(80), index=True)
    size: Mapped[str] = mapped_column(String(80))
    image_url: Mapped[str] = mapped_column(Text)
    purchase_price: Mapped[int] = mapped_column(Integer)
    shipping_price: Mapped[int] = mapped_column(Integer)
    total_price_rub: Mapped[int] = mapped_column(Integer)
    avito_price: Mapped[int] = mapped_column(Integer)
    expected_profit: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(40))
    seller_is_suspicious: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    authenticity_risk: Mapped[str] = mapped_column(String(40), default="low", nullable=False)
    source_url: Mapped[str] = mapped_column(Text)

    favorites = relationship("Favorite", back_populates="item", cascade="all, delete-orphan")
    instruction = relationship("Instruction", back_populates="item", uselist=False, cascade="all, delete-orphan")
