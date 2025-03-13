from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.core.exceptions.http_exceptions import (
    DuplicateValueException,
    NotFoundException,
)
from app.dao import BaseDAO
from app.schemas.review import (
    ReviewRead,
    ReviewFilter,
    ReviewCreate,
    ReviewUpdate,
    ReviewCreateInternal,
    ReviewCategoryCreateInternal,
    ReviewCategoryRatingUpdate,
    ReviewCategoryRatingCreate,
    ReviewCategoryRatingFilter,
)
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

    @classmethod
    async def create_hotel_review(
        cls,
        session: AsyncSession,
        review_create_data: ReviewCreate,
        hotel_id: int,
        user_id: int,
    ):
        db_review = await ReviewDAO.get_one_or_none(
            session=session,
            filters=ReviewFilter(
                hotel_id=hotel_id,
                user_id=user_id,
            ),
        )
        if db_review:
            raise DuplicateValueException("User already has a review for this hotel")

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
        if len(review_create_data.category_ratings) > 0:
            for review_category_rating in review_create_data.category_ratings:
                review_category_rating_create_data = ReviewCategoryCreateInternal(
                    review_category_id=review_category_rating.review_category_id,
                    rating=review_category_rating.rating,
                    review_id=craeted_review.id,
                )

                await ReviewCategoryRatingDAO.create(
                    session=session,
                    values=review_category_rating_create_data,
                )
        return ReviewRead.model_validate(craeted_review)

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
            raise NotFoundException("Review not found")
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
                rating_data = ReviewCategoryCreateInternal(
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
