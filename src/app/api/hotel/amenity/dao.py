from app.core.dao import BaseDAO

from .models import HotelAmenity, HotelAmenityCategory


class HotelAmenityDAO(BaseDAO):
    model = HotelAmenity


class HotelAmenityCategoryDAO(BaseDAO):
    model = HotelAmenityCategory
