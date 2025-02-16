from fastapi import (
    Depends,
)

# from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.http_exceptions import UnauthorizedException
from app.dao.user_dao import TokenBlacklistDAO, UserDAO

from ..schemas import UserBase
from .helpers import (
    TOKEN_TYPE_FIELD,
)
from .utils import decode_jwt, verify_password

http_bearer = HTTPBearer(auto_error=False)
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def validate_token_type(
    payload: dict,
    token_type: str,
) -> bool:
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type == token_type:
        return True
    raise UnauthorizedException(
        f"Invalid token type {current_token_type!r} expected {token_type!r}"
    )


def get_current_token_payload(
    access_token: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> dict:
    try:
        # Получаем токен из схемы bearer
        token = access_token.credentials if access_token else None
        if not token:
            raise UnauthorizedException("Access token missing")
        payload = decode_jwt(
            token=token,
        )
    except InvalidTokenError:
        raise UnauthorizedException("Invalid access token")
    return payload


def get_current_token_payload_for_optional_user(
    access_token: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> dict | None:
    try:
        # Получаем токен из схемы bearer
        token = access_token.credentials if access_token else None
        if not token:
            return None

        payload = decode_jwt(
            token=token,
        )
        return payload
    except (InvalidTokenError, AttributeError):
        return None


async def get_refresh_token_payload(
    session: AsyncSession,
    refresh_token: str,
) -> dict:
    if not refresh_token:
        raise UnauthorizedException("Refresh token missing")
    try:
        payload = decode_jwt(
            token=refresh_token,
        )
        # Проверяем, не в черном ли списке токен
        if await TokenBlacklistDAO.is_token_blacklisted(
            session=session,
            jti=payload.get("jti"),
        ):
            raise UnauthorizedException("Token is blacklisted")
        return payload
    except InvalidTokenError as e:
        raise UnauthorizedException(f"Invalid refresh token: {e}")


async def get_user_by_token_sub(session: AsyncSession, payload: dict) -> UserBase:
    user_id: str | None = payload.get("sub")
    # todo: check token blacklist
    jti = payload.get("jti")
    is_blacklisted = await TokenBlacklistDAO.get_one_or_none_by_id(
        session=session,
        data_id=jti,
    )
    if is_blacklisted:
        raise UnauthorizedException("Invalid token (blacklisted)")
    if not user_id:
        raise UnauthorizedException("Invalid token (user not found)")
    try:
        user_id_int = int(user_id)
    except ValueError:
        raise UnauthorizedException("Invalid token format")

    user = await UserDAO.find_one_or_none(
        session=session,
        id=user_id_int,
    )
    if user:
        return user
    raise UnauthorizedException("Invalid token (user not found)")


async def authenticate_user(
    phone_number: str,
    password: str,
    session: AsyncSession,
) -> UserBase | None:

    db_user = await UserDAO.find_one_or_none(
        db=session,
        phone_number=phone_number,
        is_superuser=True,
    )
    if not db_user:
        return None

    elif not await verify_password(
        password=password,
        hashed_password=db_user["hashed_password"],
    ):
        return None

    return db_user
