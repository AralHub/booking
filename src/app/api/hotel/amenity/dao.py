from app.core.dao import BaseDAO

from .models import Amenity


class AmenityDAO(BaseDAO):
    model = Amenity
