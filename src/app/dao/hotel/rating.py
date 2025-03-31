from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BaseDAO
from app.core.exceptions.http_exceptions import NotFoundException
from app.models.hotel.info import HotelInfo
from app.models.hotel import Hotel
from app.models.review import Review, ReviewCategory, ReviewCategoryRating
from app.models.hotel.rating import HotelCategoryRating, HotelRating
from app.dao.base import BaseDAO
from app.models.review import Review
from app.schemas.review import ReviewFilter
from app.schemas.hotel.rating import (
    HotelRatingCreateInternal,
    HotelCategoryRatingCreateInternal,
)


class HotelCategoryRatingDAO(BaseDAO):
    model = HotelCategoryRating


class HotelRatingDAO(BaseDAO):
    model = HotelRating

    @staticmethod
    async def _get_review_count_for_hotel(
        cls,
        session: AsyncSession,
        hotel_id: int,
    ) -> int:
        result = await session.execute(
            select(func.count(Review.id)).where(Review.hotel_id == hotel_id)
        )
        return result.unique().scalar_one_or_none()

    @classmethod
    async def get_hotel_summary_rating(
        cls,
        session: AsyncSession,
        hotel_id: int,
    ):
        # Получаем существующий рейтинг
        hotel_rating = await session.execute(
            select(HotelRating)
            .options(joinedload(HotelRating.category_ratings))
            .where(HotelRating.hotel_id == hotel_id)
            .where(HotelCategoryRating.hotel_rating_id == HotelRating.id)
        )
        rating = hotel_rating.unique().scalar_one_or_none()

        return rating if rating else []

    @classmethod
    async def create_hotel_sum_rating(
        cls,
        session: AsyncSession,
        hotel_id: int,
    ):
        # Общий средний рейтинг
        general_rating = await session.execute(
            select(func.avg(Review.rating)).where(Review.hotel_id == hotel_id)
        )
        avg_general = general_rating.scalar() or 0
        reviews_count = await cls._get_review_count_for_hotel(
            cls,
            session=session,
            hotel_id=hotel_id,
        )
        # Рейтинги по категориям
        result = await session.execute(
            select(
                ReviewCategory.id,
                func.avg(ReviewCategoryRating.rating).label("avg_rating"),
            )
            .join(ReviewCategoryRating.review_category)
            .join(Review, ReviewCategoryRating.review_id == Review.id)
            .where(Review.hotel_id == hotel_id)
            .group_by(ReviewCategory.id)
        )
        category_ratings = (
            result.fetchall()
        )  # без await, так как result.fetchall() возвращает обычный список

        hotel_rating = await cls.create(
            session=session,
            values=HotelRatingCreateInternal(
                average_rating=avg_general,
                reviews_count=reviews_count,
                hotel_id=hotel_id,
            ),
        )
        # Создаем записи для каждой категории
        for category in category_ratings:
            await HotelCategoryRatingDAO.create(
                session=session,
                values=HotelCategoryRatingCreateInternal(
                    rating=category.avg_rating or 0,
                    review_category_id=category.id,
                    hotel_rating_id=hotel_rating.id,
                ),
            )
