from app.core import SessionDep
from app.core.exceptions.http_exceptions import NotFoundException
from app.core.i18n.translations import ErrorCode
from app.core.logger import logging
from app.dao.hotel.category import HotelCategoryDAO

logger = logging.getLogger(__name__)


async def validate_hotel_category_by_id(
    category_id: int,
    session=SessionDep,
):
    hotel_category = await HotelCategoryDAO.get_one_or_none_by_id(
        session=session,
        data_id=category_id,
    )
    if not hotel_category:
        raise NotFoundException(ErrorCode.NOT_FOUND)
    return hotel_category
