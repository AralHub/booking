from fastapi import APIRouter, Depends, Query

from app.api.dependencies.hotel import validate_hotel
from app.api.dependencies.review import validate_review_owner
from app.api.dependencies.user import get_current_active_auth_user
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings
from app.dao.hotel.rating import HotelRatingDAO
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
    tags=["Hotel Rating"],
    prefix=settings.api_v1.hotel_prefix,
)


@router.get("/{hotel_id}/rating")
async def get_hotel_rating(
    hotel_id: int,
    session=SessionDep,
):

    hotel_rating = await HotelRatingDAO.get_hotel_summary_rating(
        session=session,
        hotel_id=hotel_id,
    )
    return hotel_rating

