from app.core.dao import BaseDAO
from app.models.rule import Rule


class RuleDAO(BaseDAO):
    model = Rule
