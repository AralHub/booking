from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BaseDAO
from app.models.room.images import RoomImage


class RoomImageDAO(BaseDAO):
    model = RoomImage

