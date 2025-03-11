from app.dao import BaseDAO
from app.core.exceptions.http_exceptions import NotFoundException

from app.models.hotel import HotelCategory, HotelInfo


class HotelCategoryDAO(BaseDAO):
    model = HotelCategory


class HotelInfoDAO(BaseDAO):
    model = HotelInfo
