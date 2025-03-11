from app.dao import BaseDAO
from app.models.room.types import RoomType


class RoomTypeDAO(BaseDAO):
    model = RoomType
