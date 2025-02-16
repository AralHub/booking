from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.models import User, TokenBlacklist
from app.auth.schemas import (
    UserFilter,
    UserRead,
    TokenBlacklistFilter,
    TokenBlacklistCreate,
)
from app.dao.base_dao import BaseDAO
from app.core.exceptions.http_exceptions import NotFoundException
from app.auth.functions.utils import decode_jwt
from datetime import UTC, datetime


class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def get_user_by_phone(
        cls,
        session: AsyncSession,
        phone_number: str,
    ) -> UserRead | None:
        user = await cls.get_one_or_none(
            session=session,
            filters=UserFilter(phone_number=phone_number),
        )
        if not user:
            raise NotFoundException(detail="User not found")
        return UserRead.model_validate(user)


class TokenBlacklistDAO(BaseDAO):
    model = TokenBlacklist

    @classmethod
    async def add_to_blacklist(
        cls,
        token: str,
        session: AsyncSession,
    ) -> None:
        payload = decode_jwt(token)
        expires_at = datetime.fromtimestamp(
            payload.get("exp"),
            tz=UTC,
        )
        await cls.create(
            session=session,
            values=TokenBlacklistCreate(
                **{
                    "jti": payload.get("jti"),
                    "expires_at": expires_at,
                    "is_blacklisted": True,
                }
            ),
        )

    @classmethod
    async def is_token_blacklisted(
        cls,
        session: AsyncSession,
        jti: str,
    ) -> bool:
        """Проверяет, находится ли токен в черном списке"""
        token = await cls.find_one_or_none(
            session=session,
            filters=TokenBlacklistFilter(jti=jti),
        )
        return token.is_blacklisted if token else False
