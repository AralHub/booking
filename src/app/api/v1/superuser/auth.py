from fastapi import APIRouter, Response

from app.core import SessionDep
from app.core.auth.helpers import (
    create_access_token,
    create_refresh_token,
)
from app.core.auth.validation import authenticate_user
from app.core.config import settings
from app.core.exceptions.http_exceptions import (
    UnauthorizedException,
)
from app.schemas.user import (
    LoginUser,
    TokenInfo,
)

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=TokenInfo)
async def superuser_login(
    login_data: LoginUser,
    response: Response,
    session=SessionDep,
):
    user = await authenticate_user(
        phone_number=login_data.phone_number,
        password=login_data.password,
        session=session,
    )
    if not user:
        raise UnauthorizedException("Wrong phone number or password.")
    access_token = await create_access_token(user)
    refresh_token = await create_refresh_token(user)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=settings.crypt.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
    )
