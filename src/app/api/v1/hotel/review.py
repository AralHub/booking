from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.api.dependencies.hotel import validate_hotel_by_slug
from app.api.dependencies.review import (
    validate_review_owner_by_slug,
)
from app.api.dependencies.user import get_current_active_auth_user
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings
from app.core.exceptions.http_exceptions import (
    BadRequestException,
    DuplicateValueException,
)
from app.core.i18n.responses import (
    RESPONSE_MESSAGES,
    BaseResponse,
)
from app.core.i18n.translations import ErrorCode
from app.dao.booking import BookingDAO
from app.dao.hotel.review import ReviewDAO
from app.schemas.hotel.info import HotelNameRead
from app.schemas.review import (
    ReviewCreate,
    ReviewFilter,
    ReviewRead,
    ReviewUpdate,
)
from app.schemas.user import UserRead

router = APIRouter(
    tags=["Hotel Reviews"],
    prefix=settings.api_v1.hotel_prefix,
)


@router.get(
    "/{hotel_slug}/reviews",
)
async def get_hotel_reviews(
    hotel_slug: str,
    page: int = Query(default=1, ge=1, description="Номер страницы"),
    page_size: int = Query(default=10, ge=1, le=100, description="Размер страницы"),
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    session=SessionDep,
):
    hotel_reviews = await ReviewDAO.get_all_hotel_reviews(
        session=session,
        hotel_id=hotel.id,
        page=page,
        page_size=page_size,
        order_by="created_at",
        order_direction="desc",
    )
    return hotel_reviews


@router.post(
    "/{hotel_slug}/reviews",
)
async def create_hotel_reviews(
    hotel_slug: str,
    review_create_data: ReviewCreate,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    current_user: UserRead = Depends(get_current_active_auth_user),
    session=TransactionSessionDep,
):
    completed_bookings = await BookingDAO.get_user_completed_bookings(
        session=session,
        user_id=current_user.id,
        hotel_id=hotel.id,
        current_date=datetime.today().date(),
    )

    if not completed_bookings:
        raise BadRequestException(
            error_code=ErrorCode.BAD_REQUEST,
            message="Вы можете оставить отзыв только после завершенной брони в этом отеле",
        )
    existing_review = await ReviewDAO.get_one_or_none(
        session=session,
        filters=ReviewFilter(
            user_id=current_user.id,
            hotel_id=hotel.id,
        ),
    )
    if existing_review:
        raise DuplicateValueException(
            error_code=ErrorCode.DUPLICATE_VALUE,
            message="Вы уже оставили отзыв в этом отеле",
        )
    created_review = await ReviewDAO.create_hotel_review(
        session=session,
        review_create_data=review_create_data,
        hotel_id=hotel.id,
        user_id=current_user.id,
    )
    return {
        "data": created_review,
    }


@router.put(
    "/{hotel_slug}/reviews/{review_id}",
)
async def update_hotel_review(
    hotel_slug: str,
    review_id: int,
    review_update_data: ReviewUpdate,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    review: ReviewRead = Depends(validate_review_owner_by_slug),
    session=TransactionSessionDep,
):
    updated_review = await ReviewDAO.update_hotel_review(
        session=session,
        hotel_id=hotel.id,
        user_id=review.user_id,
        review_id=review_id,
        review_update_data=review_update_data,
    )
    return {
        "data": updated_review,
    }


@router.delete(
    "/{hotel_slug}/reviews/{review_id}",
    response_model=BaseResponse,
)
async def delete_hotel_review(
    hotel_slug: str,
    review_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    review: ReviewRead = Depends(validate_review_owner_by_slug),
    session=TransactionSessionDep,
):
    await ReviewDAO.delete(
        session=session,
        filters=ReviewFilter(
            id=review_id,
            user_id=review.user_id,
            hotel_id=hotel.id,
        ),
    )
    return BaseResponse(
        success=True,
        message=RESPONSE_MESSAGES.get(
            "DATA_DELETED",
            "Hotel review deleted successfully",
        ),
    )
