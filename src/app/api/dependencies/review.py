from fastapi import Depends

from app.core import SessionDep
from app.core.exceptions.http_exceptions import (
    NotFoundException,
    UnauthorizedException,
)
from app.core.i18n.translations import ErrorCode
from app.core.logger import logging
from app.dao.hotel.review import ReviewDAO
from app.schemas.hotel.info import HotelNameRead
from app.schemas.user import UserRead

from .hotel import validate_hotel, validate_hotel_by_slug
from .user import get_current_auth_user

logger = logging.getLogger(__name__)


async def validate_review_owner(
    review_id: int,
    hotel: HotelNameRead = Depends(validate_hotel),
    current_user: UserRead = Depends(get_current_auth_user),
    session=SessionDep,
):
    db_review = await ReviewDAO.get_one_or_none_by_id(
        session=session,
        data_id=review_id,
    )
    if not db_review:
        raise NotFoundException(ErrorCode.NOT_FOUND)
    if db_review.user_id != current_user.id:
        raise UnauthorizedException(ErrorCode.UNAUTHORIZED)
    return db_review


async def validate_review_owner_by_slug(
    review_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    current_user: UserRead = Depends(get_current_auth_user),
    session=SessionDep,
):
    db_review = await ReviewDAO.get_one_or_none_by_id(
        session=session,
        data_id=review_id,
        hotel_id=hotel.id,
    )
    if not db_review:
        raise NotFoundException(ErrorCode.NOT_FOUND)
    if db_review.user_id != current_user.id:
        raise UnauthorizedException(ErrorCode.UNAUTHORIZED)
    return db_review
