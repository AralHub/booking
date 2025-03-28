from fastapi import APIRouter, Depends, Response, status
from jwt import InvalidTokenError

from app.api.dependencies.user import get_current_auth_user
from app.core import SessionDep, TransactionSessionDep
from app.core.auth.helpers import (
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
)
from app.core.auth.utils import hash_password
from app.core.auth.validation import (
    authenticate_user,
    get_refresh_token_payload,
    get_user_by_token_sub,
    validate_token_type,
)
from app.core.config import settings
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
from app.dao.user import TokenBlacklistDAO, UserDAO
from app.schemas.user import (
    LoginUser,
    RefreshToken,
    TokenInfo,
    UserCreate,
    UserCreateInternal,
    UserFilter,
    UserUpdateInternal,
    VerifyPhoneNumber,
)

REFRESH_TOKEN_KEY = "refresh_token"
router = APIRouter(prefix=settings.api.auth)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user_data: UserCreate,
    session=TransactionSessionDep,
):
    # Проверяем, существует ли партнер, до отправки SMS
    db_user = await UserDAO.get_user_by_phone(
        session=session,
        phone_number=user_data.phone_number,
    )

    # Если партнер уже существует и верифицирован/активен, возвращаем ошибку
    if db_user and (db_user.is_verified or db_user.is_active):
        raise DuplicateValueException(
            error_code=ErrorCode.USER_ALREADY_EXISTS,
        )

    # Отправляем SMS только если нужно регистрировать партнера
    success, message = await send_verification_sms(user_data.phone_number)
    if not success:
        raise TooManyRequestsException(message)

    # Хешируем пароль один раз
    hashed_password = hash_password(user_data.password).decode("utf-8")

    # Подготавливаем общие данные для создания партнера
    user_create_data = UserCreateInternal(
        **user_data.model_dump(exclude={"password"}),
        password=hashed_password,
        is_active=False,
        is_verified=False,
        is_fully_registered=False,
    )

    # Если партнер существует, но не верифицирован и не активен - удаляем его
    if db_user:
        await UserDAO.delete(
            session=session,
            filters=UserFilter(id=db_user.id),
        )

    # Создаем нового партнера
    await UserDAO.create(
        session=session,
        values=user_create_data,
    )

    return {
        "message": "Verification code sent successfully",
        "phone_number": user_data.phone_number,
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
    db_user = await UserDAO.get_user_by_phone(
        session=session,
        phone_number=verify_data.phone_number,
    )
    if not db_user:
        raise NotFoundException(
            ErrorCode.USER_NOT_FOUND,
        )
    await UserDAO.update(
        session=session,
        filters=UserFilter(id=db_user.id),
        values=UserUpdateInternal(
            is_active=True,
            is_verified=True,
            is_fully_registered=True,
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


@router.post("/login", response_model=TokenInfo)
async def user_login(
    login_data: LoginUser,
    response: Response,
    session=SessionDep,
):
    db_user = await authenticate_user(
        phone_number=login_data.phone_number,
        password=login_data.password,
        session=session,
    )
    if not db_user:
        raise UnauthorizedException("Wrong phone number or password.")
    access_token = await create_access_token(db_user)
    refresh_token = await create_refresh_token(db_user)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=settings.crypt.REFRESH_TOKEN_HTTPONLY,
        secure=settings.crypt.REFRESH_TOKEN_COOKIE_SECURE,
        samesite=settings.crypt.REFRESH_TOKEN_COOKIE_SAMESITE,
        max_age=settings.crypt.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
    )


@router.post(
    "/logout",
    dependencies=[Depends(get_current_auth_user)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    response: Response,
    refresh_token_data: RefreshToken,
    session=TransactionSessionDep,
):
    try:
        token = refresh_token_data.refresh_token
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
    refresh_token_data: RefreshToken,
    session=SessionDep,
):
    token = refresh_token_data.refresh_token
    if not token:
        raise UnauthorizedException("Refresh token is missing")
    payload = await get_refresh_token_payload(
        session=session,
        refresh_token=token,
    )
    validate_token_type(payload, REFRESH_TOKEN_TYPE)
    db_user = await get_user_by_token_sub(
        session=session,
        payload=payload,
    )
    new_access_token = await create_access_token(db_user)
    return TokenInfo(
        access_token=new_access_token,
        token_type="Bearer",
    )
