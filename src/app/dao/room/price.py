from app.dao import BaseDAO

from app.models.room import RoomPrice


class RoomPriceDAO(BaseDAO):
    model = RoomPrice
