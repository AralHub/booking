# from sqlalchemy.ext.asyncio import AsyncSession
from app.api.hotel.models import Hotel, HotelCategory
from app.core.dao import BaseDAO


class HotelDAO(BaseDAO):
    model = Hotel


class HotelCategoryDAO(BaseDAO):
    model = HotelCategory
