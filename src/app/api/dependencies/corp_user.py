from fastapi import (
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db_helper
from app.core.auth.helpers import ACCESS_TOKEN_TYPE
from app.core.auth.validation import (
    get_corp_user_by_token_sub,
    get_current_token_payload,
    validate_token_type,
)
from app.core.exceptions.http_exceptions import (
    UnauthorizedException,
)
from app.core.logger import logging
from app.schemas.corp_user import CorpUserBase

logger = logging.getLogger(__name__)


class CorpUserGetterFromToken:
    def __init__(self, token_type: str):
        self.token_type = token_type

    async def __call__(
        self,
        payload: dict = Depends(get_current_token_payload),
        session: AsyncSession = Depends(db_helper.session_getter),
    ):
        validate_token_type(payload, self.token_type)
        corp_user = await get_corp_user_by_token_sub(session, payload)
        if not corp_user:
            raise UnauthorizedException("Inactive corp user")
        return corp_user


get_current_auth_corp_user = CorpUserGetterFromToken(ACCESS_TOKEN_TYPE)


async def get_current_active_corp_user(
    corp_user: CorpUserBase = Depends(get_current_auth_corp_user),
):
    if corp_user.is_active:
        return corp_user
    raise UnauthorizedException("Inactive corp user")
