from app.dao import BaseDAO
from app.models.hotel.rules import HotelRule


class HotelRuleDAO(BaseDAO):
    model = HotelRule
