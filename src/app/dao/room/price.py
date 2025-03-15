from app.dao import BaseDAO

from app.models.room.price import RoomPrice


class RoomPriceDAO(BaseDAO):
    model = RoomPrice
