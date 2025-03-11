# from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BaseDAO

from app.models.language import Language


class LanguageDAO(BaseDAO):
    model = Language
