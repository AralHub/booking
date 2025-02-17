from sqlalchemy.ext.asyncio import AsyncSession
from app.hotel.models import Hotel, Room
from app.core.exceptions.http_exceptions import NotFoundException
from app.auth.functions.utils import decode_jwt
from datetime import UTC, datetime
from .base_dao import BaseDAO


class HotelDAO(BaseDAO):
    model = Hotel


class RoomDAO(BaseDAO):
    model = Room
