from fastapi import APIRouter, Depends, Query

from app.api.dependencies.hotel import validate_hotel_by_slug
from app.api.dependencies.review import (
    validate_review_owner_by_slug,
)
from app.api.dependencies.user import get_current_active_auth_user
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings
from app.core.i18n.responses import (
    RESPONSE_MESSAGES,
    BaseResponse,
    DataResponse,
    ListResponse,
)
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
    response_model=ListResponse[ReviewRead],
)
async def get_hotel_reviews(
    hotel_slug: str,
    page: int = Query(default=1, ge=1, description="Номер страницы"),
    page_size: int = Query(default=10, ge=1, le=100, description="Размер страницы"),
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    session=SessionDep,
):
    hotel_reviews = await ReviewDAO.paginate(
        session=session,
        filters=ReviewFilter(
            hotel_id=hotel.id,
        ),
        page=page,
        page_size=page_size,
        order_by="created_at",
        order_direction="desc",
    )
    return ListResponse[ReviewRead](
        data=hotel_reviews,
    )


@router.post(
    "/{hotel_slug}/reviews",
    response_model=DataResponse[ReviewRead],
)
async def create_hotel_reviews(
    hotel_slug: str,
    review_create_data: ReviewCreate,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    current_user: UserRead = Depends(get_current_active_auth_user),
    session=TransactionSessionDep,
):
    created_review = await ReviewDAO.create_hotel_review(
        session=session,
        review_create_data=review_create_data,
        hotel_id=hotel.id,
        user_id=current_user.id,
    )
    return DataResponse[ReviewRead](
        data=created_review,
        message=RESPONSE_MESSAGES.get(
            "DATA_CREATED",
            "Hotel review created successfully",
        ),
    )


@router.put(
    "/{hotel_slug}/reviews/{review_id}",
    response_model=DataResponse[ReviewRead],
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
    return DataResponse[ReviewRead](
        data=updated_review,
        message=RESPONSE_MESSAGES.get(
            "DATA_UPDATED",
            "Hotel review updated successfully",
        ),
    )


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
