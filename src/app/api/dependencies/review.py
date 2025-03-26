from fastapi import Depends

from app.core import SessionDep
from app.core.exceptions.http_exceptions import (
    NotFoundException,
    UnauthorizedException,
)
from app.core.logger import logging
from app.dao.review import ReviewDAO
from app.schemas.hotel.info import HotelNameRead
from app.schemas.user import UserRead

from .hotel import validate_hotel_id
from .user import get_current_auth_user

logger = logging.getLogger(__name__)


async def validate_review_owner_by_id(
    review_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_id),
    current_user: UserRead = Depends(get_current_auth_user),
    session=SessionDep,
):
    db_review = await ReviewDAO.get_one_or_none_by_id(
        session=session,
        data_id=review_id,
    )
    if not db_review:
        raise NotFoundException("Review not found")
    if db_review.user_id != current_user.id:
        raise UnauthorizedException("Permission denied")
    return db_review
