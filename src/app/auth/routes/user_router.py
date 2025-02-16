from datetime import UTC, datetime

from fastapi import APIRouter, Depends

from app.auth.schemas import (
    UserProfileCreate,
    UserRead,
    UserUpdateInternal,
)
from app.core import TransactionSessionDep
from app.core.config import settings
from app.dao import UserDAO

from ..dependencies import get_current_active_auth_user
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


async def create_user_profile(
    user_profile: UserProfileCreate,
    payload: dict = Depends(get_current_token_payload),
    session=TransactionSessionDep,
):
    user_id = int(payload.get("sub"))
    update_user_profile = UserUpdateInternal(
        **user_profile.model_dump(),
        is_active=True,
        is_fully_registered=True,
        updated_at=datetime.now(UTC),
        id=user_id,
    )
    updated_profile = await UserDAO.update(
        db=session,
        filters=update_user_profile,
    )
    return updated_profile


@router.patch("/phone-number/")
async def change_phone_number():
    pass


@router.post("/phone-number/verify/")
async def verify_phone_number():
    pass


@router.delete(
    "/{user_id}",
)
async def auth_user_delete():
    pass
