from app.auth.model import User
from app.auth.schema import UserFilter, UserSchema
from app.dao.base_dao import BaseDAO
from sqlalchemy.ext.asyncio import AsyncSession


class UserDAO(BaseDAO):
    model = User
