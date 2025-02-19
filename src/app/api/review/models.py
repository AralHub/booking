from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin, TimestampMixin

if TYPE_CHECKING:
    from ..user.models import User  # noqa
    from app.api.hotel.models import Hotel  # noqa


class ReviewCategory(IntIdPkMixin, Base):
    __tablename__ = "review_categories"
    name: Mapped[str] = mapped_column(String(30))

    # relationships
    review_category_ratings = relationship(
        "ReviewCategoryRating",
        back_populates="review_category",
    )


class Review(IntIdPkMixin, TimestampMixin, Base):
    rating: Mapped[float] = mapped_column(Float)
    comment: Mapped[str] = mapped_column(Text)

    # relationships
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    hotel = relationship(
        "Hotel",
        back_populates="reviews",
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user = relationship(
        "User",
        back_populates="reviews",
    )
    review_category_ratings = relationship(
        "ReviewCategoryRating",
        back_populates="review",
    )


class ReviewCategoryRating(IntIdPkMixin, Base):
    """Модель для хранения оценок по категориям"""

    rating: Mapped[float] = mapped_column(Float)

    # relationships
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id"))
    review = relationship(
        "Review",
        back_populates="review_category_ratings",
    )

    review_category_id: Mapped[int] = mapped_column(
        ForeignKey("review_categories.id"),
    )
    review_category = relationship(
        "ReviewCategory",
        back_populates="review_category_ratings",
    )
