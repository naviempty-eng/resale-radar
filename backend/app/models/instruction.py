from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Instruction(Base):
    __tablename__ = "instructions"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"), unique=True, index=True)
    content: Mapped[str] = mapped_column(Text)

    item = relationship("Item", back_populates="instruction")
