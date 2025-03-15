from fastapi import APIRouter, Depends, Query

from app.api.dependencies.hotel import validate_hotel_id, validate_review_owner_by_id
from app.api.dependencies.user import get_current_active_auth_user
from app.core import SessionDep, TransactionSessionDep
from app.dao.review import ReviewDAO
from app.schemas.hotel.info import HotelNameRead
from app.schemas.review import (
    HotelReviewSummary,
    ReviewCreate,
    ReviewFilter,
    ReviewRead,
    ReviewUpdate,
)
from app.schemas.user import UserRead

router = APIRouter(
    tags=["Hotel Reviews"],
)


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


@router.get("/{hotel_id}/reviews")
async def get_hotel_reviews(
    hotel_id: int,
    page: int = Query(default=1, ge=1, description="Номер страницы"),
    page_size: int = Query(default=10, ge=1, le=100, description="Размер страницы"),
    hotel: HotelNameRead = Depends(validate_hotel_id),
    session=SessionDep,
):
    results = await ReviewDAO.paginate(
        session=session,
        filters=ReviewFilter(
            hotel_id=hotel_id,
        ),
        page=page,
        page_size=page_size,
        order_by="created_at",
        order_direction="desc",
    )
    return [ReviewRead.model_validate(item) for item in results]


@router.post("/{hotel_id}/reviews")
async def create_hotel_reviews(
    hotel_id: int,
    review_create_data: ReviewCreate,
    hotel: HotelNameRead = Depends(validate_hotel_id),
    current_user: UserRead = Depends(get_current_active_auth_user),
    session=TransactionSessionDep,
):
    await ReviewDAO.create_hotel_review(
        session=session,
        review_create_data=review_create_data,
        hotel_id=hotel_id,
        user_id=current_user.id,
    )


@router.put("/{hotel_id}/reviews/{review_id}")
async def update_hotel_review(
    hotel_id: int,
    review_id: int,
    review_update_data: ReviewUpdate,
    hotel: HotelNameRead = Depends(validate_hotel_id),
    current_user: UserRead = Depends(get_current_active_auth_user),
    session=TransactionSessionDep,
):
    await ReviewDAO.update_hotel_review(
        session=session,
        hotel_id=hotel_id,
        user_id=current_user.id,
        review_id=review_id,
        review_update_data=review_update_data,
    )


@router.delete("/{hotel_id}/reviews/{review_id}")
async def delete_hotel_review(
    hotel_id: int,
    review_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_id),
    review: ReviewRead = Depends(validate_review_owner_by_id),
    session=TransactionSessionDep,
):
    await ReviewDAO.delete(
        session=session,
        filters=ReviewFilter(
            id=review_id,
        ),
    )
