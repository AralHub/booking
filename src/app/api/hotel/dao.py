# from sqlalchemy.ext.asyncio import AsyncSession
from app.api.hotel.models import Hotel, HotelCategory
from app.api.hotel.room.models import Room, RoomType
from app.core.dao import BaseDAO


class HotelDAO(BaseDAO):
    model = Hotel


class HotelCategoryDAO(BaseDAO):
    model = HotelCategory


class RoomDAO(BaseDAO):
    model = Room


class RoomTypeDAO(BaseDAO):
    model = RoomType
