# from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dao import BaseDAO

from .models import Review


class ReviewDAO(BaseDAO):
    model = Review
