from datetime import timedelta

from app.core.config import settings
from app.schemas.corp_user import CorpUserBase
from app.schemas.partner import PartnerBase
from app.schemas.user import UserBase

from .utils import encode_jwt

TOKEN_TYPE_FIELD = settings.crypt.TOKEN_TYPE_FIELD
ACCESS_TOKEN_TYPE = settings.crypt.ACCESS_TOKEN_TYPE
REFRESH_TOKEN_TYPE = settings.crypt.REFRESH_TOKEN_TYPE


async def create_jwt(
    token_type: str,
    token_data: dict,
    expire_minutes: int = settings.crypt.ACCESS_TOKEN_EXPIRE_MINUTES,
    expire_timedelta: timedelta | None = None,
) -> str:
    jwt_payload = {
        TOKEN_TYPE_FIELD: token_type,
    }
    jwt_payload.update(token_data)
    return encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )


async def create_access_jwt(jwt_payload: dict):
    return await create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=settings.crypt.ACCESS_TOKEN_EXPIRE_MINUTES,
    )


async def create_refresh_jwt(jwt_payload: dict):
    return await create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=settings.crypt.REFRESH_TOKEN_EXPIRE_DAYS),
    )


async def create_access_token(user: UserBase) -> str:
    jwt_payload = {
        "sub": str(user.id),
        "first_name": user.first_name,
        "role": "user",
    }
    return await create_access_jwt(jwt_payload)


async def create_refresh_token(user: UserBase) -> str:
    jwt_payload = {
        "sub": str(user.id),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": "user",
    }
    return await create_refresh_jwt(jwt_payload)


async def create_access_token_partner(partner: PartnerBase) -> str:
    jwt_payload = {
        "sub": str(partner.id),
        "first_name": partner.first_name,
        "role": "partner",
    }
    return await create_access_jwt(jwt_payload)


async def create_refresh_token_partner(partner: PartnerBase) -> str:
    jwt_payload = {
        "sub": str(partner.id),
        "first_name": partner.first_name,
        "last_name": partner.last_name,
        "role": "partner",
    }
    return await create_refresh_jwt(jwt_payload)


async def create_access_token_corp_user(corp_user: CorpUserBase) -> str:
    jwt_payload = {
        "sub": str(corp_user.id),
        "first_name": corp_user.first_name,
        "role": "corp_user",
    }
    return await create_access_jwt(jwt_payload)


async def create_refresh_token_corp_user(corp_user: CorpUserBase) -> str:
    jwt_payload = {
        "sub": str(corp_user.id),
        "first_name": corp_user.first_name,
        "last_name": corp_user.last_name,
        "role": "corp_user",
    }
    return await create_refresh_jwt(jwt_payload)
