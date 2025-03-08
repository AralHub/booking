from fastapi import APIRouter

from app.api.user.schemas import LoginUser

# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
from app.core import TransactionSessionDep

from .schemas import (
    PartnerCreate,
)

router = APIRouter(
    tags=["Partner"],
    prefix="/partner",
)


@router.post("/register")
async def create_hotel_admin(
    hotel_admin_create_data: PartnerCreate,
    session=TransactionSessionDep,
):
    pass


@router.post("/login")
async def login_hotel_admin(
    hotel_admin_login_data: LoginUser,
    session=TransactionSessionDep,
):
    pass
