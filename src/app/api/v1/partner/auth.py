from typing import Optional

from fastapi import APIRouter, Depends, Request, Response, status
from jwt import InvalidTokenError

from app.api.dependencies.partner import get_current_auth_partner

# from app.core.utils.eskiz_client import code_generator
from app.core import SessionDep, TransactionSessionDep
from app.core.auth.helpers import (
    REFRESH_TOKEN_TYPE,
    create_access_token_partner,
    create_refresh_token_partner,
)
from app.core.auth.utils import hash_password
from app.core.auth.validation import (
    authenticate_partner,
    get_partner_by_token_sub,
    get_refresh_token_payload,
    validate_token_type,
)
from app.core.exceptions.http_exceptions import (
    BadRequestException,
    DuplicateValueException,
    NotFoundException,
    TooManyRequestsException,
    UnauthorizedException,
)
from app.core.i18n.translations import ErrorCode
from app.core.utils import redis_sms
from app.core.utils.send_sms import send_verification_sms
from app.dao.partner import PartnerDAO
from app.dao.user import TokenBlacklistDAO
from app.schemas.partner import (
    PartnerCreate,
    PartnerCreateInternal,
    PartnerFilter,
    PartnerUpdateInternal,
)
from app.schemas.user import (
    LoginUser,
    RefreshToken,
    TokenInfo,
    VerifyPhoneNumber,
)

REFRESH_TOKEN_KEY = "refresh_token"

router = APIRouter(
    tags=["Partners"],
    prefix="/auth",
)

from app.core.i18n.responses import (
    RESPONSE_MESSAGES,
    DataResponse,
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=DataResponse[dict],
)
async def register_partner(
    partner_data: PartnerCreate,
    session=TransactionSessionDep,
):
    # Проверяем, существует ли партнер, до отправки SMS
    db_partner = await PartnerDAO.get_partner_by_phone(
        session=session,
        phone_number=partner_data.phone_number,
    )

    # Если партнер уже существует и верифицирован/активен, возвращаем ошибку
    if db_partner and (db_partner.is_verified or db_partner.is_active):
        raise DuplicateValueException(
            error_code=ErrorCode.USER_ALREADY_EXISTS,
        )

    # Отправляем SMS только если нужно регистрировать партнера
    success, _ = await send_verification_sms(partner_data.phone_number)
    if not success:
        raise TooManyRequestsException(
            error_code=ErrorCode.TOO_MANY_REQUESTS,
        )

    # Хешируем пароль один раз
    hashed_password = hash_password(partner_data.password).decode("utf-8")

    # Подготавливаем общие данные для создания партнера
    partner_create_data = PartnerCreateInternal(
        **partner_data.model_dump(
            exclude={"password"},
            exclude_none=True,
        ),
        password=hashed_password,
        is_active=False,
        is_verified=False,
        is_fully_registered=False,
    )

    # Если партнер существует, но не верифицирован и не активен - удаляем его
    if db_partner:
        await PartnerDAO.delete(
            session=session,
            filters=PartnerFilter(id=db_partner.id),
        )

    # Создаем нового партнера
    await PartnerDAO.create(
        session=session,
        values=partner_create_data,
    )

    return DataResponse(
        data={"phone_number": partner_data.phone_number},
        message=RESPONSE_MESSAGES["AUTH_CODE_SENT"],
        success=True,
    )


@router.post(
    "/verify",
    status_code=status.HTTP_201_CREATED,
    response_model=DataResponse[TokenInfo],
)
async def verify_phone_number(
    response: Response,
    verify_data: VerifyPhoneNumber,
    session=TransactionSessionDep,
):
    success, _ = await redis_sms.verify_sms_code(
        phone=verify_data.phone_number,
        code=verify_data.code,
    )
    if not success:
        raise BadRequestException(error_code=ErrorCode.BAD_REQUEST)
    # Проверяем, существует ли пользователь
    db_partner = await PartnerDAO.get_partner_by_phone(
        session=session,
        phone_number=verify_data.phone_number,
    )
    if not db_partner:
        raise NotFoundException(
            ErrorCode.USER_NOT_FOUND,
        )
    await PartnerDAO.update(
        session=session,
        filters=PartnerFilter(id=db_partner.id),
        values=PartnerUpdateInternal(
            is_active=True,
            is_verified=True,
            is_fully_registered=True,
        ),
    )
    # Создаем токены
    access_token = await create_access_token_partner(db_partner)
    refresh_token = await create_refresh_token_partner(db_partner)
    return DataResponse(
        message=RESPONSE_MESSAGES["PHONE_VERIFIED"],
        success=True,
        data=TokenInfo(
            access_token=access_token,
            refresh_token=refresh_token,
        ),
    )


@router.post(
    "/login",
    response_model=DataResponse[TokenInfo],
)
async def partner_login(
    login_data: LoginUser,
    response: Response,
    session=SessionDep,
):
    db_partner = await authenticate_partner(
        phone_number=login_data.phone_number,
        password=login_data.password,
        session=session,
    )
    if not db_partner:
        raise UnauthorizedException("Wrong phone number or password.")
    access_token = await create_access_token_partner(db_partner)
    refresh_token = await create_refresh_token_partner(db_partner)

    return DataResponse(
        data=TokenInfo(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
        ),
    )


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
    response_model=DataResponse[TokenInfo],
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
    new_access_token = await create_access_token_partner(partner)
    return DataResponse(
        data=TokenInfo(
            access_token=new_access_token,
            token_type="Bearer",
        ),
    )
