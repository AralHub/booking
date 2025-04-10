from sqlalchemy import select

from app.core import SessionDep
from app.core.exceptions.http_exceptions import (
    NotFoundException,
)
from app.core.i18n.translations import ErrorCode
from app.core.logger import logging
from app.models.hotel import Hotel

logger = logging.getLogger(__name__)


async def validate_active_hotel(
    hotel_id: int,
    session=SessionDep,
):
    query = select(Hotel).filter_by(id=hotel_id)
    result = await session.execute(query)
    db_hotel = result.unique().scalar_one_or_none()
    if not db_hotel:
        raise NotFoundException(
            detail="Hotel not found",
            error_code=ErrorCode.HOTEL_NOT_FOUND,
        )
    if not db_hotel.is_active:
        raise NotFoundException(
            detail="Hotel not found",
            error_code=ErrorCode.HOTEL_NOT_FOUND,
        )
    return db_hotel


async def validate_hotel(
    hotel_id: int,
    session=SessionDep,
):
    query = select(Hotel).filter_by(id=hotel_id)
    result = await session.execute(query)
    db_hotel = result.unique().scalar_one_or_none()
    if not db_hotel:
        logger.error(f"Hotel not found: {hotel_id}")
        raise NotFoundException(error_code=ErrorCode.HOTEL_NOT_FOUND)
    return db_hotel


async def validate_hotel_by_slug(
    hotel_slug: str,
    session=SessionDep,
):
    query = select(Hotel).filter_by(slug=hotel_slug)
    result = await session.execute(query)
    db_hotel = result.unique().scalar_one_or_none()
    if not db_hotel:
        logger.error(f"Hotel not found: {hotel_slug}")
        raise NotFoundException(error_code=ErrorCode.HOTEL_NOT_FOUND)
    return db_hotel
