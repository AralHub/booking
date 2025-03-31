from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import IntIdPkMixin, TimestampMixin, MultilingualNameMixin

if TYPE_CHECKING:
    from app.models.user import User  # noqa
    from app.models.hotel import Hotel  # noqa


class ReviewCategory(
    IntIdPkMixin,
    MultilingualNameMixin,
    Base,
):
    # relationships
    review_category_ratings = relationship(
        "ReviewCategoryRating",
        back_populates="review_category",
    )


class ReviewCategoryRating(IntIdPkMixin, Base):
    rating: Mapped[float] = mapped_column(Float)

    review_category_id: Mapped[int] = mapped_column(
        ForeignKey("review_categories.id"),
    )
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id"))
    # relationships

    review = relationship(
        "Review",
        back_populates="review_category_ratings",
    )

    review_category = relationship(
        "ReviewCategory",
        back_populates="review_category_ratings",
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
