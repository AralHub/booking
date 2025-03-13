from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.dao import BaseDAO
from app.schemas.review import ReviewFilter
from app.models.review import Review, ReviewCategory, ReviewCategoryRating


class ReviewCategoryDAO(BaseDAO):
    model = ReviewCategory


class ReviewCategoryRatingDAO(BaseDAO):
    model = ReviewCategoryRating


class ReviewDAO(BaseDAO):
    model = Review

    @classmethod
    async def get_all_hotel_reviews(cls, session: AsyncSession, hotel_id: int):
        reviews_query = (
            select(Review)
            .options(joinedload(Review.review_category_ratings))
            .where(Review.hotel_id == hotel_id)
        )
        reviews = await session.execute(reviews_query)
        return reviews.unique().scalars().all()

    @classmethod
    async def get_hotel_review_summary(
        cls, session: AsyncSession, hotel_id: int
    ) -> dict:
        # Общий средний рейтинг
        general_rating = await session.execute(
            select(func.avg(Review.rating)).where(Review.hotel_id == hotel_id)
        )
        avg_general = general_rating.scalar() or 0

        # Рейтинги по категориям
        category_ratings = await session.execute(
            select(
                ReviewCategory.name,
                func.avg(ReviewCategoryRating.rating).label("avg_rating"),
            )
            .join(ReviewCategoryRating.review_category)
            .where(ReviewCategoryRating.review_id == Review.id)
            .where(Review.hotel_id == hotel_id)
            .group_by(ReviewCategory.name)
        )

        return {
            "general_rating": round(avg_general, 1),
            "category_ratings": {
                row.name: round(row.avg_rating, 1) for row in category_ratings
            },
        }

    @classmethod
    async def get_review_count_for_hotel(
        cls,
        session: AsyncSession,
        hotel_id: int,
    ) -> int:
        review_count = await cls.count(
            session=session,
            filters=ReviewFilter(
                hotel_id=hotel_id,
            ),
        )
        return review_count
