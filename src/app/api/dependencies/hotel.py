from fastapi import Depends
from sqlalchemy import select

from app.api.dependencies.partner import get_current_auth_partner
from app.api.dependencies.user import get_current_auth_user
from app.core import SessionDep
from app.core.exceptions.http_exceptions import (
    NotFoundException,
    UnauthorizedException,
)
from app.dao.review import ReviewDAO
from app.models.hotel import Hotel
from app.models.room import Room
from app.schemas.hotel.info import HotelNameRead
from app.schemas.partner import PartnerRead
from app.schemas.user import UserRead
from app.core.i18n.translations import ErrorCode

async def validate_active_hotel(
    hotel_id: int,
    session=SessionDep,
):
    query = select(Hotel).filter_by(id=hotel_id)
    result = await session.execute(query)
    db_hotel = result.unique().scalar_one_or_none()
    if not db_hotel:
        raise NotFoundException(error_code=ErrorCode.HOTEL_NOT_FOUND)
    if not db_hotel.is_active:
        raise NotFoundException(error_code=ErrorCode.HOTEL_NOT_FOUND)
    return db_hotel


async def validate_hotel_id(
    hotel_id: int,
    session=SessionDep,
):
    query = select(Hotel).filter_by(id=hotel_id)
    result = await session.execute(query)
    db_hotel = result.unique().scalar_one_or_none()
    if not db_hotel:
        raise NotFoundException(error_code=ErrorCode.HOTEL_NOT_FOUND)
    return db_hotel


async def validate_hotel_room_id(
    room_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_id),
    session=SessionDep,
):
    query = select(Room).filter_by(id=room_id, hotel_id=hotel.id)
    result = await session.execute(query)
    db_room = result.unique().scalar_one_or_none()
    if not db_room:
        raise NotFoundException(error_code=ErrorCode.ROOM_NOT_FOUND)
    return db_room


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


async def valid_hotel_admin(
    hotel: HotelNameRead = Depends(validate_hotel_id),
    current_partner: PartnerRead = Depends(get_current_auth_partner),
):
    if hotel.hotel_admin_id != current_partner.id:
        raise UnauthorizedException("Permission denied")
    return hotel
