from app.core.config import settings
from fastapi import APIRouter

from app.api.hotel.dao import HotelDAO

# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
from app.core import SessionDep, TransactionSessionDep
from app.core.exceptions.http_exceptions import NotFoundException

from .dao import HotelAdminDAO
from .schemas import (
    PartnerLogin,
    PartnerCreate,
    PartnerCreateInternal,
    PartnerFilter,
    PartnerRead,
)

router = APIRouter(
    tags=["Partner"],
    prefix="/partner",
)


@router.post("/register")
async def create_hotel_admin(
    hotel_admin_create_data: HotelAdminCreate,
    session=TransactionSessionDep,
):
    pass


@router.post("/login")
async def login_hotel_admin(
    hotel_admin_login_data: HotelAdminLogin,
    session=TransactionSessionDep,
):
    pass
