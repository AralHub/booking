from app.core.dao import BaseDAO

from .models import Partner


class PartnerDAO(BaseDAO):
    model = Partner
