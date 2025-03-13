from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel_id
from app.api.dependencies.user import get_current_active_auth_user
from app.core import SessionDep, TransactionSessionDep
from app.dao.review import ReviewCategoryRatingDAO, ReviewDAO
from app.schemas.hotel.info import HotelNameRead
from app.schemas.review import (
    ReviewCategoryCreateInternal,
    ReviewCreate,
    ReviewCreateInternal,
    HotelReviewSummary,
)
from app.schemas.user import UserRead

router = APIRouter(
    tags=["Hotel Reviews"],
)


@router.get("/{hotel_id}/reviews")
async def get_hotel_reviews(
    hotel_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_id),
    session=SessionDep,
):
    return await ReviewDAO.get_all_hotel_reviews(
        session=session,
        hotel_id=hotel_id,
    )


@router.post("/{hotel_id}/reviews")
async def create_hotel_reviews(
    hotel_id: int,
    review_create_data: ReviewCreate,
    hotel: HotelNameRead = Depends(validate_hotel_id),
    current_user: UserRead = Depends(get_current_active_auth_user),
    session=TransactionSessionDep,
):

    craeted_review = await ReviewDAO.create(
        session=session,
        values=ReviewCreateInternal(
            **review_create_data.model_dump(
                exclude={
                    "category_ratings",
                }
            ),
            hotel_id=hotel_id,
            user_id=current_user.id,
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
    return craeted_review


@router.get("/{hotel_id}/reviews/summary")
async def get_hotel_review_summary(
    hotel_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_id),
    session=SessionDep,
):
    summary_data = await ReviewDAO.get_hotel_review_summary(
        session=session,
        hotel_id=hotel_id,
    )

    # Получаем количество отзывов
    review_count = await ReviewDAO.get_review_count_for_hotel(
        session=session,
        hotel_id=hotel_id,
    )

    return HotelReviewSummary(
        general_rating=summary_data["general_rating"],
        review_count=review_count,
        category_ratings=summary_data["category_ratings"],
    )
