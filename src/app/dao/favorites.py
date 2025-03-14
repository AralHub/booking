# from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BaseDAO

from app.models.favorites import UserFavorite


class UserFavoriteDAO(BaseDAO):
    model = UserFavorite
