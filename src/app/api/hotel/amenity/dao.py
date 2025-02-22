from app.core.dao import BaseDAO

from .models import (
    HotelAmenity,
    HotelAmenityCategory,
    RoomAmenity,
    RoomAmenityCategory,
)


class HotelAmenityDAO(BaseDAO):
    model = HotelAmenity


class HotelAmenityCategoryDAO(BaseDAO):
    model = HotelAmenityCategory


class RoomAmenityCategoryDAO(BaseDAO):
    model = RoomAmenityCategory


class RoomAmenityDAO(BaseDAO):
    model = RoomAmenity
