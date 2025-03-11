# from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dao import BaseDAO

from .models import Language


class LanguageDAO(BaseDAO):
    model = Language
