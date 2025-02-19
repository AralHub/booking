from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin, TimestampMixin

if TYPE_CHECKING:
    pass


class ReviewCategory(IntIdPkMixin, Base):
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
        "Hotels",
        back_populates="reviews",
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user = relationship(
        "Users",
        back_populates="review",
    )
    review_category_ratings = relationship(
        "ReviewCategoryRating",
        back_populates="review",
    )


class ReviewCategoryRating(IntIdPkMixin, Base):
    """Модель для хранения оценок по категориям"""

    rating: Mapped[float] = mapped_column(Float)

    # relationships
    review_id: Mapped[int] = mapped_column(ForeignKey("review.id"))
    review = relationship(
        "Review",
        back_populates="review_category_ratings",
    )

    review_category_id: Mapped[int] = mapped_column(
        ForeignKey("review_category.id"),
    )
    review_category = relationship(
        "ReviewCategory",
        back_populates="review_category_ratings",
    )
