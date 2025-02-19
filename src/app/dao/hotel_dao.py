from sqlalchemy.ext.asyncio import AsyncSession
from app.api.hotel.models import Hotel, HotelCategory
from app.api.hotel.room.models import Room, RoomType
from app.core.exceptions.http_exceptions import NotFoundException
from app.api.user.functions.utils import decode_jwt
from datetime import UTC, datetime
from .base_dao import BaseDAO


class HotelDAO(BaseDAO):
    model = Hotel


class HotelCategoryDAO(BaseDAO):
    model = HotelCategory


class RoomDAO(BaseDAO):
    model = Room


class RoomTypeDAO(BaseDAO):
    model = RoomType
