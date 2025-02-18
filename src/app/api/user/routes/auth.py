from typing import Optional

from fastapi import APIRouter, Depends, Request, Response, status, HTTPException
from jwt import InvalidTokenError

from app.api.user.schemas import (
    RefreshToken,
    TokenInfo,
    UserFilter,
    UserCreate,
    UserCreateInternal,
    UserUpdateInternal,
    VerifyPhoneNumber,
)

# from app.core.utils.eskiz_client import code_generator
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings
from app.core.exceptions.http_exceptions import (
    BadRequestException,
    NotFoundException,
    TooManyRequestsException,
    UnauthorizedException,
)
from app.core.utils import redis_sms, task_queue
from app.dao import TokenBlacklistDAO, UserDAO

from ..functions.dependencies import get_current_auth_user
from ..functions.helpers import (
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
)
from ..functions.validation import (
    get_refresh_token_payload,
    get_user_by_token_sub,
    validate_token_type,
)

router = APIRouter(
    tags=["Auth"],
    prefix=settings.api.auth,
)
REFRESH_TOKEN_KEY = "refresh_token"


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    register_data: UserCreate,
    session=TransactionSessionDep,
):
    code = "12345"
    # code = await code_generator()
    success, message = await redis_sms.save_sms_code(
        phone=register_data.phone_number,
        code=code,
    )
    if not success:
        raise TooManyRequestsException(message)
    message = f"{settings.eskiz.ESKIZ_TEMPLATE_TEXT} {code}"
    # await task_queue.pool.enqueue_job(
    #     "send_sms_task",
    #     message=message,
    #     phone_number=user_phone_number.phone_number,
    # )
    await task_queue.pool.enqueue_job(
        "send_sms_code",
        message=message,
        phone_number=register_data.phone_number,
    )
    # Проверяем, существует ли пользователь
    db_user = await UserDAO.get_user_by_phone(
        session=session,
        phone_number=register_data.phone_number,
    )
    if db_user:
        raise BadRequestException("User already exists")
    await UserDAO.create(
        session=session,
        values=UserCreateInternal(
            **register_data.model_dump(),
            is_active=False,
            is_verified=False,
            is_fully_registered=False,
        ),
    )
    return {
        "message": "Verification code sent successfully",
        "phone_number": register_data.phone_number,
    }


@router.post(
    "/verify/",
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
    db_user = await UserDAO.get_user_by_phone(
        session=session,
        phone_number=verify_data.phone_number,
    )
    if not db_user:
        raise NotFoundException("User not found")
    user_internal_dict = verify_data.model_dump()
    del user_internal_dict["code"]
    await UserDAO.update(
        session=session,
        filters=UserFilter(
            id=db_user.id,
        ),
        values=UserUpdateInternal(
            is_verified=True,
        ),
    )
    # Создаем токены
    access_token = await create_access_token(db_user)
    refresh_token = await create_refresh_token(db_user)
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
        "is_fully_registered": db_user.is_fully_registered,
    }


@router.post(
    "/refresh/",
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
    user = await get_user_by_token_sub(
        session=session,
        payload=payload,
    )
    new_access_token = await create_access_token(user)
    return TokenInfo(
        access_token=new_access_token,
        token_type="Bearer",
    )


@router.post(
    "/logout/",
    dependencies=[Depends(get_current_auth_user)],
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
