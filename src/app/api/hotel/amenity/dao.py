from app.core.dao import BaseDAO

from .models import Amenity, AmenityCategory


class AmenityDAO(BaseDAO):
    model = Amenity


class AmenityCategoryDAO(BaseDAO):
    model = AmenityCategory
