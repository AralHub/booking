from app.core import SessionDep
from app.core.exceptions.http_exceptions import (
    NotFoundException,
)
from app.core.i18n.translations import ErrorCode
from app.dao.hotel.amenities import HotelAmenityCategoryDAO, HotelAmenityDAO
from app.dao.room.amenities import RoomAmenityCategoryDAO, RoomAmenityDAO


async def validate_hotel_amenities_category(
    category_id: int,
    session=SessionDep,
):
    hotel_amenities_category = await HotelAmenityCategoryDAO.get_one_or_none_by_id(
        session=session,
        data_id=category_id,
    )
    if not hotel_amenities_category:
        raise NotFoundException(error_code=ErrorCode.NOT_FOUND)
    return hotel_amenities_category


async def validate_hotel_amenity(
    amenity_id: int,
    session=SessionDep,
):
    hotel_amenity = await HotelAmenityDAO.get_one_or_none_by_id(
        session=session,
        data_id=amenity_id,
    )
    if not hotel_amenity:
        raise NotFoundException(error_code=ErrorCode.NOT_FOUND)
    return hotel_amenity


async def validate_room_amenities_category(
    category_id: int,
    session=SessionDep,
):
    room_amenities_category = await RoomAmenityCategoryDAO.get_one_or_none_by_id(
        session=session,
        data_id=category_id,
    )
    if not room_amenities_category:
        raise NotFoundException(error_code=ErrorCode.NOT_FOUND)
    return room_amenities_category


async def validate_room_amenity(
    amenity_id: int,
    session=SessionDep,
):
    room_amenity = await RoomAmenityDAO.get_one_or_none_by_id(
        session=session,
        data_id=amenity_id,
    )
    if not room_amenity:
        raise NotFoundException(error_code=ErrorCode.NOT_FOUND)
    return room_amenity
