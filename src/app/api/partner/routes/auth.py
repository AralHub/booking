from typing import Optional

from fastapi import APIRouter, Depends, Request, Response, status
from jwt import InvalidTokenError

from app.api.user.dao import TokenBlacklistDAO
from app.api.user.schemas import (
    PhoneNumber,
    RefreshToken,
    TokenInfo,
    VerifyPhoneNumber,
)

# from app.core.utils.eskiz_client import code_generator
from app.core import SessionDep, TransactionSessionDep
from app.core.auth.helpers import (
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
)
from app.core.auth.validation import (
    get_partner_by_token_sub,
    get_refresh_token_payload,
    validate_token_type,
)
from app.core.config import settings
from app.core.exceptions.http_exceptions import (
    BadRequestException,
    NotFoundException,
    TooManyRequestsException,
    UnauthorizedException,
)

# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
# from app.core.utils.eskiz_client import code_generator
from app.core.utils import redis_sms
from app.core.utils.send_sms import send_verification_sms

from ..dao import PartnerDAO
from ..dependencies import get_current_auth_partner
from ..schemas import (
    PartnerFilter,
    PartnerUpdateInternal,
)

REFRESH_TOKEN_KEY = "refresh_token"

router = APIRouter(
    tags=["Partners"],
    prefix="/auth",
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def register_partner(
    partner_data: PhoneNumber,
):
    success, message = await send_verification_sms(partner_data.phone_number)
    if not success:
        raise TooManyRequestsException(message)
    return {
        "message": "Verification code sent successfully",
        "phone_number": partner_data.phone_number,
    }


@router.post(
    "/verify",
    status_code=status.HTTP_201_CREATED,
)
async def verify_phone_number(
    response: Response,
    verify_data: VerifyPhoneNumber,
    session=TransactionSessionDep,
):
    success, message = await redis_sms.verify_sms_code(
        phone=verify_data.phone_number,
        code=verify_data.code,
    )
    if not success:
        raise BadRequestException(message)
    # Проверяем, существует ли пользователь
    db_partner = await PartnerDAO.get_partner_by_phone(
        session=session,
        phone_number=verify_data.phone_number,
    )
    if not db_partner:
        raise NotFoundException("User not found")

    await PartnerDAO.update(
        session=session,
        filters=PartnerFilter(
            id=db_partner.id,
        ),
        values=PartnerUpdateInternal(
            phone_number=verify_data.phone_number,
            is_active=True,
            is_verified=True,
            is_fully_registered=True,
        ),
    )
    # Создаем токены
    access_token = await create_access_token(db_partner)
    refresh_token = await create_refresh_token(db_partner)
    response.delete_cookie(key="refresh_token")
    response.set_cookie(
        key=REFRESH_TOKEN_KEY,
        value=refresh_token,
        httponly=settings.crypt.REFRESH_TOKEN_HTTPONLY,
        secure=settings.crypt.REFRESH_TOKEN_COOKIE_SECURE,
        samesite=settings.crypt.REFRESH_TOKEN_COOKIE_SAMESITE,
        max_age=settings.crypt.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )
    return {
        "tokens": TokenInfo(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
        ),
        "is_fully_registered": db_partner.is_fully_registered,
    }


@router.post(
    "/logout",
    dependencies=[Depends(get_current_auth_partner)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    request: Request,
    response: Response,
    refresh_token_data: Optional[RefreshToken] = None,
    session=TransactionSessionDep,
):
    try:
        token = refresh_token_data.refresh_token or request.cookies.get(
            REFRESH_TOKEN_KEY
        )
        if not token:
            raise UnauthorizedException("Refresh token is missing")
        await TokenBlacklistDAO.add_to_blacklist(
            session=session,
            token=token,
        )
        response.delete_cookie(key=REFRESH_TOKEN_KEY)

        return {
            "message": "Logged out successfully",
        }

    except InvalidTokenError:
        raise UnauthorizedException("Invalid token")


@router.post(
    "/refresh",
    response_model=TokenInfo,
    status_code=status.HTTP_201_CREATED,
)
async def refresh_access_token(
    request: Request,
    refresh_token_data: RefreshToken,
    session=SessionDep,
):
    token = refresh_token_data.refresh_token or request.cookies.get(REFRESH_TOKEN_KEY)
    if not token:
        raise UnauthorizedException("Refresh token is missing")
    payload = await get_refresh_token_payload(
        session=session,
        refresh_token=token,
    )
    validate_token_type(payload, REFRESH_TOKEN_TYPE)
    partner = await get_partner_by_token_sub(
        session=session,
        payload=payload,
    )
    new_access_token = await create_access_token(partner)
    return TokenInfo(
        access_token=new_access_token,
        token_type="Bearer",
    )
