from app.core import SessionDep
from app.core.exceptions.http_exceptions import (
    NotFoundException,
)
from app.core.i18n.translations import ErrorCode
from app.dao.hotel.amenities import HotelAmenityCategoryDAO, HotelAmenityDAO


async def validate_hotel_amenities_category(
    category_id: int,
    session=SessionDep,
):
    hotel_amenities_category = await HotelAmenityCategoryDAO.get_one_or_none_by_id(
        session=session,
        data_id=category_id,
    )
    if not hotel_amenities_category:
        raise NotFoundException(ErrorCode.NOT_FOUND)
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
        raise NotFoundException(ErrorCode.NOT_FOUND)
    return hotel_amenity
