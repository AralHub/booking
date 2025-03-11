from app.dao import BaseDAO
from app.core.exceptions.http_exceptions import NotFoundException

from app.models.hotel.info import HotelInfo


class HotelInfoDAO(BaseDAO):
    model = HotelInfo
