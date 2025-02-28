from app.core.dao import BaseDAO

from .models import HotelAdmin, HotelAdminInfo


class HotelAdminDAO(BaseDAO):
    model = HotelAdmin


class HotelAdminInfoDAO(BaseDAO):
    model = HotelAdminInfo
