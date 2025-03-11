from app.dao import BaseDAO
from app.models.hotel.rules import Rule


class RuleDAO(BaseDAO):
    model = Rule
