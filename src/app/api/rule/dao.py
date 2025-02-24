from app.core.dao import BaseDAO
from .models import Rule


class RuleDAO(BaseDAO):
    model = Rule
