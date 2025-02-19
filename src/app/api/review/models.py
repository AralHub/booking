from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin, TimestampMixin

if TYPE_CHECKING:
    pass


class Review(IntIdPkMixin, TimestampMixin, Base):

    rating: Mapped[float] = mapped_column(Float)
    comment: Mapped[str] = mapped_column(Text)
    # relationships
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    hotel = relationship(
        "Hotels",
        back_populates="reviews",
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user = relationship(
        "Users",
        back_populates="review",
    )
