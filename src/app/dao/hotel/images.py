from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BaseDAO
from app.models.hotel.images import HotelImage


class HotelImageDAO(BaseDAO):
    model = HotelImage
