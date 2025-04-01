from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import IntIdPkMixin

if TYPE_CHECKING:
    from app.models.hotel import Hotel


class HotelCategoryRating(IntIdPkMixin, Base):
    hotel_rating_id: Mapped[int] = mapped_column(ForeignKey("hotel_ratings.id"))
    rating: Mapped[float] = mapped_column(Float)
    review_category_id: Mapped[int] = mapped_column(ForeignKey("review_categories.id"))

    # relationships
    hotel_rating = relationship(
        "HotelRating",
        back_populates="category_ratings",
    )


class HotelRating(IntIdPkMixin, Base):
    average_rating: Mapped[float] = mapped_column(Float)
    reviews_count: Mapped[int] = mapped_column(Integer)

    # relationships
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    hotel: Mapped["Hotel"] = relationship(
        "Hotel",
        back_populates="hotel_rating",
    )
    category_ratings: Mapped[list["HotelCategoryRating"]] = relationship(
        back_populates="hotel_rating",
        cascade="all, delete-orphan",
    )
