from app.core.dao import BaseDAO

from .models import HotelAdmin


class HotelAdminDAO(BaseDAO):
    model = HotelAdmin
