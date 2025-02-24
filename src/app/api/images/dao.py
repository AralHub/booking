from app.api.images.models import HotelImage, RoomImage
from app.core.dao import BaseDAO


class HotelImageDAO(BaseDAO):
    model = HotelImage


class RoomImageDAO(BaseDAO):
    model = RoomImage
