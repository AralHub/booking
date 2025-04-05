from sqlalchemy.ext.asyncio import AsyncSession

from app.dao import BaseDAO
from app.models.company import Company


class CompanyDAO(BaseDAO):
    model = Company
