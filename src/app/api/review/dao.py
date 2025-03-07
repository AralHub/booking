from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.dao import BaseDAO

from .models import Review, ReviewCategory, ReviewCategoryRating


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


class ReviewCategoryDAO(BaseDAO):
    model = ReviewCategory


class ReviewCategoryRatingDAO(BaseDAO):
    model = ReviewCategoryRating
