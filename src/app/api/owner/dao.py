from app.core.dao import BaseDAO

from .models import HotelOwner, HotelOwnerInfo


class HotelOwnerDAO(BaseDAO):
    model = HotelOwner


class HotelOwnerInfoDAO(BaseDAO):
    model = HotelOwnerInfo
