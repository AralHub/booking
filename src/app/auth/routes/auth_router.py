from typing import Optional

from fastapi import APIRouter, Request, Response, status

# from app.core.utils.eskiz_client import code_generator
from app.auth.schemas import (
    RefreshToken,
    TokenInfo,
    UserCreateViaPhoneNumberInternal,
    UserPhoneNumber,
    UserVerifyPhoneNumber,
)
from app.core.config import settings
from app.core.db.session_maker import SessionDep, TransactionSessionDep
from app.core.exceptions.http_exceptions import (
    BadRequestException,
    TooManyRequestsException,
    UnauthorizedException,
)
from app.core.utils import redis_sms, task_queue
from app.dao.user_dao import UserDAO

from ..functions import helpers, validation
from ..functions.helpers import REFRESH_TOKEN_TYPE

router = APIRouter(
    tags=["Auth"],
    prefix=settings.api.auth,
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user_phone_number: UserPhoneNumber,
):
    code = "12345"
    # code = await code_generator()
    success, message = await redis_sms.save_sms_code(
        phone=user_phone_number.phone_number,
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
        phone_number=user_phone_number.phone_number,
    )
    return {
        "message": "Verification code sent successfully",
        "phone_number": user_phone_number.phone_number,
    }


@router.post(
    "/verify/",
    status_code=status.HTTP_201_CREATED,
)
async def verify_phone_number(
    response: Response,
    verify_data: UserVerifyPhoneNumber,
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
        user_internal_dict = verify_data.model_dump()
        del user_internal_dict["code"]
        user_internal_dict["is_fully_registered"] = False
        user_internal_dict["name"] = f"user{verify_data.phone_number[-4:]}"
        user_internal = UserCreateViaPhoneNumberInternal(**user_internal_dict)
        new_user = await UserDAO.add(
            session=session,
            object=user_internal,
        )
        db_user = new_user.to_dict()
    # Создаем токены
    access_token = await helpers.create_access_token(db_user)
    refresh_token = await helpers.create_refresh_token(db_user)
    response.delete_cookie(key="refresh_token")
    response.set_cookie(
        key="refresh_token",
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
        "is_fully_registered": db_user["is_fully_registered"],
    }


@router.post(
    "/refresh/",
    response_model=TokenInfo,
    status_code=status.HTTP_201_CREATED,
)
async def refresh_access_token(
    request: Request,
    refresh_token_data: Optional[RefreshToken] = None,
    session=SessionDep,
):
    token = refresh_token_data.refresh_token or request.cookies.get("refresh_token")
    if not token:
        raise UnauthorizedException("Refresh token is missing")
    payload = await validation.get_refresh_token_payload(
        session=session,
        refresh_token=token,
    )
    validation.validate_token_type(payload, REFRESH_TOKEN_TYPE)
    user = await validation.get_user_by_token_sub(
        session=session,
        payload=payload,
    )
    new_access_token = await helpers.create_access_token(user)
    return TokenInfo(
        access_token=new_access_token,
        token_type="Bearer",
    )


@router.post(
    "/logout/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout_user(
    request: Request,
):
    pass
