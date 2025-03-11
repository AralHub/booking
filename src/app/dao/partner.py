from sqlalchemy.ext.asyncio import AsyncSession

from app.dao import BaseDAO
from app.models.partner import Partner
from app.schemas.partner import PartnerFilter, PartnerRead


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
