from fastapi import APIRouter, status

# from app.core.utils.eskiz_client import code_generator
from app.core import TransactionSessionDep
from app.core.auth.utils import hash_password
from app.core.exceptions.http_exceptions import (
    DuplicateValueException,
    TooManyRequestsException,
)
from app.core.i18n.translations import ErrorCode
from app.core.utils.send_sms import send_verification_sms
from app.dao.corp_user import CorpUserDAO
from app.schemas.corp_user import (
    CorpUserCrateInternal,
    CorpUserCreate,
    CorpUserFilter,
)

REFRESH_TOKEN_KEY = "refresh_token"

router = APIRouter(
    prefix="/auth",
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def register_partner(
    corp_user_data: CorpUserCreate,
    session=TransactionSessionDep,
):
    # Проверяем, существует ли партнер, до отправки SMS
    db_corp_user = await CorpUserDAO.get_corp_user_by_phone(
        session=session,
        phone_number=corp_user_data.phone_number,
    )

    # Если партнер уже существует и верифицирован/активен, возвращаем ошибку
    if db_corp_user and (db_corp_user.is_verified or db_corp_user.is_active):
        raise DuplicateValueException(
            detail="Corp user already exists",
            error_code=ErrorCode.USER_ALREADY_EXISTS,
        )

    # Отправляем SMS только если нужно регистрировать партнера
    success, message = await send_verification_sms(corp_user_data.phone_number)
    if not success:
        raise TooManyRequestsException(message)

    # Хешируем пароль один раз
    hashed_password = hash_password(corp_user_data.password).decode("utf-8")

    # Подготавливаем общие данные для создания партнера
    corp_user_create_data = CorpUserCrateInternal(
        **corp_user_data.model_dump(exclude={"password"}),
        password=hashed_password,
        is_active=False,
        is_verified=False,
        is_fully_registered=False,
    )

    # Если партнер существует, но не верифицирован и не активен - удаляем его
    if db_corp_user and not (db_corp_user.is_verified or db_corp_user.is_active):
        await CorpUserDAO.delete(
            session=session,
            filters=CorpUserFilter(id=db_corp_user.id),
        )

    # Создаем нового партнера
    await CorpUserDAO.create(
        session=session,
        values=corp_user_create_data,
    )

    return {
        "message": "Verification code sent successfully",
        "phone_number": corp_user_data.phone_number,
    }
