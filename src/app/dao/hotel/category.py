from app.dao import BaseDAO

from app.models.hotel.category import HotelCategory


class HotelCategoryDAO(BaseDAO):
    model = HotelCategory
