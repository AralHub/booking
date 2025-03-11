from app.dao import BaseDAO


from app.models.room import Room
from app.models.room.bed import BedType, RoomBedConfiguration


class BedTypeDAO(BaseDAO):
    model = BedType


class RoomBedConfDAO(BaseDAO):
    model = RoomBedConfiguration
