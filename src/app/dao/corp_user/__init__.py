from sqlalchemy.ext.asyncio import AsyncSession

from app.dao import BaseDAO
from app.models.corp_user import CorpUser
from app.models.corp_user.company import Company
from app.schemas.corp_user import CorpUserRead, CorpUserFilter


class CompanyDAO(BaseDAO):
    model = Company


class CorpUserDAO(BaseDAO):
    model = CorpUser

    @classmethod
    async def get_corp_user_by_phone(
        cls,
        session: AsyncSession,
        phone_number: str,
    ) -> CorpUserRead | None:
        corp_user = await cls.get_one_or_none(
            session=session,
            filters=CorpUserFilter(phone_number=phone_number),
        )
        return corp_user if corp_user else None
