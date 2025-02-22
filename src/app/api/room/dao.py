from app.api.room.models import Room, RoomType
from app.core.dao import BaseDAO


class RoomDAO(BaseDAO):
    model = Room


class RoomTypeDAO(BaseDAO):
    model = RoomType
