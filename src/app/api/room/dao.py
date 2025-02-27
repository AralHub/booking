from app.core.dao import BaseDAO
from .models import Room, RoomType, RoomTypeVariant


class RoomDAO(BaseDAO):
    model = Room


class RoomTypeDAO(BaseDAO):
    model = RoomType


class RoomTypeVariantDAO(BaseDAO):
    model = RoomTypeVariant
