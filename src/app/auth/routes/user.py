from datetime import UTC, datetime

from fastapi import APIRouter, Depends, status

from app.auth.schemas import (
    PhoneNumber,
    UserCreate,
    UserFilter,
    UserRead,
    UserUpdate,
    UserUpdateInternal,
    VerifyPhoneNumber,
)
from app.core import TransactionSessionDep
from app.core.config import settings
from app.core.exceptions.http_exceptions import (
    BadRequestException,
    DuplicateValueException,
    TooManyRequestsException,
)
from app.core.utils import redis_sms, task_queue
from app.dao import UserDAO

from ..functions.dependencies import get_current_active_auth_user
from ..functions.validation import get_current_token_payload

# from app.core.utils.eskiz_client import code_generator

router = APIRouter(
    tags=["User"],
    prefix=settings.api_v1.user_prefix,
)


@router.get("/me/", response_model=UserRead)
async def get_my_profile(
    user: UserRead = Depends(get_current_active_auth_user),
):
    return user


@router.post(
    "/profile/",
    status_code=status.HTTP_201_CREATED,
)
async def create_user_profile(
    user_create: UserCreate,
    payload: dict = Depends(get_current_token_payload),
    session=TransactionSessionDep,
):
    user_id = int(payload.get("sub"))
    update_user_internal = UserUpdateInternal(
        **user_create.model_dump(exclude_unset=True),
        is_active=True,
        is_fully_registered=True,
        updated_at=datetime.now(UTC),
    )
    updated_rows_count = await UserDAO.update(
        session=session,
        filters=UserFilter(id=user_id),
        values=update_user_internal,
    )
    if updated_rows_count == 0:
        raise BadRequestException("User not found")
    updated_profile = await UserDAO.get_one_or_none(
        session=session,
        filters=UserFilter(id=user_id),
    )
    return updated_profile


@router.patch("/profile/", status_code=status.HTTP_200_OK)
async def change_name(
    user_update: UserUpdate,
    current_user: UserRead = Depends(get_current_active_auth_user),
    session=TransactionSessionDep,
):
    if user_update.name == current_user.name:
        raise DuplicateValueException("The same name")

    user_update_dict = user_update.model_dump(
        exclude_unset=True,
    )
    update_internal = UserUpdateInternal(
        **user_update_dict,
    )
    updated_name = await UserDAO.update(
        session=session,
        filters=UserFilter(id=current_user.id),
        values=update_internal,
    )
    return updated_name


@router.patch("/phone-number/")
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
    code = "12345"
    # code = code_generator()
    success, message = await redis_sms.save_sms_code(
        phone=new_phone_number,
        code=code,
    )
    if not success:
        raise TooManyRequestsException(message)
    message = f"{settings.eskiz.ESKIZ_TEMPLATE_TEXT} {code}"
    # await task_queue.pool.enqueue_job(
    #     "send_sms_task",
    #     message=message,
    #     phone_number=change_phone_number.phone_number,
    # )
    await task_queue.pool.enqueue_job(
        "send_sms_code",
        message=message,
        phone_number=new_phone_number,
    )
    return {
        "message": "Verification code sent successfully",
        "phone_number": new_phone_number,
    }


@router.post("/phone-number/verify/")
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
    return {
        "message": "Phone number updated successfully",
        "phone_number": verify_data.phone_number,
    }


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def user_delete(
    current_user: UserRead = Depends(get_current_active_auth_user),
    session=TransactionSessionDep,
):
    await UserDAO.delete(
        session=session,
        filters=UserFilter(id=current_user.id),
    )
    return {
        "message": "User deleted successfully",
    }
