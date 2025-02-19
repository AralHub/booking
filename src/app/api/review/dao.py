from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dao import BaseDAO

from .models import Review
from .schemas import ReviewCreate


class ReviewDAO(BaseDAO):
    model = Review

    @classmethod
    async def create_hotel_review(
        cls,
        session: AsyncSession,
        hotel_id: int,
        user_id: int,
        comment: str,
        overall_rating: float,
        category_ratings: dict[int, float],
    ):
        review = ReviewCreate(
            hotel_id=hotel_id,
            user_id=user_id,
            comment=comment,
            rating=overall_rating,
        )
        print(review)
