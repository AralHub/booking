from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.core.exceptions.http_exceptions import (
    DuplicateValueException,
    NotFoundException,
)
from app.dao import BaseDAO
from app.core.i18n.translations import ErrorCode
from app.schemas.review import (
    ReviewRead,
    ReviewFilter,
    ReviewCreate,
    ReviewUpdate,
    ReviewCreateInternal,
    ReviewCategoryRatingCreateInternal,
    ReviewCategoryRatingUpdateInternal,
    ReviewCategoryRatingFilter,
)
from app.models.review import Review, ReviewCategory, ReviewCategoryRating
from app.dao.hotel.rating import HotelRatingDAO


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
            .options(
                joinedload(Review.review_category_ratings).joinedload(
                    ReviewCategoryRating.review_category
                )
            )
            .where(Review.hotel_id == hotel_id)
        )
        reviews = await session.execute(reviews_query)
        return reviews.unique().scalars().all()

    @classmethod
    async def create_hotel_review(
        cls,
        session: AsyncSession,
        review_create_data: ReviewCreate,
        hotel_id: int,
        user_id: int,
    ):
        try:
            db_review = await ReviewDAO.get_one_or_none(
                session=session,
                filters=ReviewFilter(
                    hotel_id=hotel_id,
                    user_id=user_id,
                ),
            )
            if db_review:
                raise DuplicateValueException(error_code=ErrorCode.DUPLICATE_VALUE)

            craeted_review = await ReviewDAO.create(
                session=session,
                values=ReviewCreateInternal(
                    **review_create_data.model_dump(
                        exclude={
                            "category_ratings",
                        }
                    ),
                    hotel_id=hotel_id,
                    user_id=user_id,
                ),
            )
            if (
                review_create_data.amenities
                and len(review_create_data.category_ratings) > 0
            ):
                for review_category_rating in review_create_data.category_ratings:
                    review_category_rating_create_data = ReviewCategoryRatingCreateInternal(
                        review_category_id=review_category_rating.review_category_id,
                        rating=review_category_rating.rating,
                        review_id=craeted_review.id,
                    )

                    await ReviewCategoryRatingDAO.create(
                        session=session,
                        values=review_category_rating_create_data,
                    )
            await HotelRatingDAO.create_hotel_sum_rating(
                session=session,
                hotel_id=hotel_id,
            )
            await session.commit()
            return ReviewRead.model_validate(craeted_review)
        except Exception as e:
            await session.rollback()
            raise e

    @classmethod
    async def update_hotel_review(
        cls,
        session: AsyncSession,
        hotel_id: int,
        user_id: int,
        review_id: int,
        review_update_data: ReviewUpdate,
    ):
        db_review = await ReviewDAO.get_one_or_none(
            session=session,
            filters=ReviewFilter(
                hotel_id=hotel_id,
                user_id=user_id,
            ),
        )
        if not db_review:
            raise NotFoundException(error_code=ErrorCode.NOT_FOUND)
        # Обновляем основные данные отзыва
        update_data = review_update_data.model_dump(
            exclude={"category_ratings"},
            exclude_unset=True,
        )
        updated_review = await cls.update(
            session=session,
            filters=ReviewFilter(
                id=review_id,
            ),
            values=ReviewUpdate(
                **update_data,
            ),
        )
        # Обновляем рейтинги категорий, если они предоставлены
        if review_update_data.category_ratings:
            review_category_rating_ids = await ReviewCategoryRatingDAO.get_all(
                session=session,
                filters=ReviewCategoryRatingFilter(
                    review_id=review_id,
                ),
            )
            await ReviewCategoryRatingDAO.delete_many(
                session=session,
                ids=[
                    review_category_rating.id
                    for review_category_rating in review_category_rating_ids
                ],
            )
            # Создаем новые рейтинги
            for category_rating in review_update_data.category_ratings:
                rating_data = ReviewCategoryRatingCreateInternal(
                    review_category_id=category_rating.review_category_id,
                    rating=category_rating.rating,
                    review_id=review_id,
                )
                await ReviewCategoryRatingDAO.create(
                    session=session,
                    values=rating_data,
                )

        updated_review = await cls.get_one_or_none(
            session=session,
            filters=ReviewFilter(id=review_id),
        )
        return ReviewRead.model_validate(updated_review)
