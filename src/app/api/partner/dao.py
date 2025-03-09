from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dao import BaseDAO

from .models import Partner
from .schemas import PartnerFilter, PartnerRead


class PartnerDAO(BaseDAO):
    model = Partner

    @classmethod
    async def get_partner_by_phone(
        cls,
        session: AsyncSession,
        phone_number: str,
    ) -> PartnerRead | None:
        partner = await cls.get_one_or_none(
            session=session,
            filters=PartnerFilter(phone_number=phone_number),
        )
        return partner if partner else None
