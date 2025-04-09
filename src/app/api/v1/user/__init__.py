import uuid as uuid_pkg
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, status

from app.api.dependencies.user import (
    get_current_active_auth_user,
    get_current_auth_user,
)
from app.core import TransactionSessionDep
from app.core.config import settings
from app.core.exceptions.http_exceptions import (
    BadRequestException,
    DuplicateValueException,
    NotFoundException,
    TooManyRequestsException,
)
from app.core.i18n.responses import RESPONSE_MESSAGES, DataResponse
from app.core.i18n.translations import ErrorCode
from app.core.utils import redis_sms
from app.core.utils.send_sms import send_verification_sms
from app.dao.user import UserDAO
from app.schemas.user import (
    PhoneNumber,
    UserFilter,
    UserRead,
    UserUpdate,
    UserUpdateInternal,
    VerifyPhoneNumber,
)

from .auth import router as auth_router

# from app.core.utils.eskiz_client import code_generator

router = APIRouter(
    tags=["Users"],
    prefix=settings.api_v1.user_prefix,
)
router.include_router(auth_router)


@router.get("/me", response_model=DataResponse[UserRead])
async def get_my_profile(
    user: UserRead = Depends(get_current_active_auth_user),
):
    return DataResponse(
        data=user,
    )


@router.put(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=DataResponse[UserRead],
)
async def update_profile(
    user_update: UserUpdate,
    current_user: UserRead = Depends(get_current_auth_user),
    session=TransactionSessionDep,
):
    user_update_dict = user_update.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )
    update_internal = UserUpdateInternal(
        **user_update_dict,
        is_active=True,
        updated_at=datetime.now(UTC),
    )
    updated_rows_count = await UserDAO.update(
        session=session,
        filters=UserFilter(id=current_user.id),
        values=update_internal,
    )
    if updated_rows_count == 0:
        raise BadRequestException("User did not update")
    updated_user = await UserDAO.get_one_or_none_by_id(
        session=session,
        data_id=current_user.id,
    )
    return DataResponse(
        data=updated_user,
        message=RESPONSE_MESSAGES.get(
            "DATA_UPDATED",
            "User updated successfully",
        ),
    )


@router.patch(
    "/me/phone-number",
    response_model=DataResponse[dict],
)
async def change_phone_number(
    user_update: PhoneNumber,
    current_user: UserRead = Depends(get_current_active_auth_user),
    session=TransactionSessionDep,
):
    new_phone_number = user_update.phone_number
    db_user = await UserDAO.get_one_or_none_by_id(
        session=session,
        data_id=current_user.id,
    )
    if new_phone_number == db_user.phone_number:
        raise DuplicateValueException("New phone number is the same as the current one")
    db_user = await UserDAO.get_one_or_none(
        session=session,
        filters=UserFilter(phone_number=new_phone_number),
    )
    if db_user:
        raise DuplicateValueException("Phone number is already registered")
    if await redis_sms.is_blocked(user_update.phone_number):
        raise TooManyRequestsException("Phone number is blocked. Try again in an hour")
    success, message = await send_verification_sms(new_phone_number)
    if not success:
        raise TooManyRequestsException(
            error_code=ErrorCode.TOO_MANY_REQUESTS,
        )
    return DataResponse(
        data={"phone_number": new_phone_number},
        message=RESPONSE_MESSAGES.get(
            "DATA_UPDATED",
            "Verification code sent successfully",
        ),
    )


@router.post(
    "/me/phone-number/verify",
    response_model=DataResponse[dict],
)
async def verify_phone_number(
    verify_data: VerifyPhoneNumber,
    current_user: UserRead = Depends(get_current_active_auth_user),
    session=TransactionSessionDep,
):
    success, message = await redis_sms.verify_sms_code(
        phone=verify_data.phone_number,
        code=verify_data.code,
    )
    if not success:
        raise BadRequestException(message)
    update_user_phone_number = UserUpdateInternal(
        phone_number=verify_data.phone_number,
    )
    updated_rows_count = await UserDAO.update(
        session=session,
        filters=UserFilter(id=current_user.id),
        values=update_user_phone_number,
    )
    if updated_rows_count == 0:
        raise BadRequestException("User not found")
    return DataResponse(
        data={"phone_number": verify_data.phone_number},
        message=RESPONSE_MESSAGES.get(
            "DATA_UPDATED",
            "Phone number updated successfully",
        ),
    )


@router.delete(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=DataResponse[dict],
)
async def user_delete(
    current_user: UserRead = Depends(get_current_active_auth_user),
    session=TransactionSessionDep,
):
    db_user = await UserDAO.get_one_or_none_by_id(
        session=session,
        data_id=current_user.id,
    )
    deleted_phone_number = f"{db_user.phone_number}_{str(uuid_pkg.uuid4())}"
    await UserDAO.update(
        session=session,
        filters=UserFilter(id=current_user.id),
        values=UserFilter(
            phone_number=deleted_phone_number,
            is_active=False,
            is_deleted=True,
            deleted_at=datetime.now(UTC),
        ),
    )
    return DataResponse(
        data={"id": db_user.id},
        message=RESPONSE_MESSAGES.get(
            "DATA_DELETED",
            "User deleted successfully",
        ),
    )
