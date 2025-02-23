
from app.core.dao import BaseDAO

from .models import (
    RoomAmenity,
    RoomAmenityCategory,
)


class RoomAmenityCategoryDAO(BaseDAO):
    model = RoomAmenityCategory


class RoomAmenityDAO(BaseDAO):
    model = RoomAmenity
