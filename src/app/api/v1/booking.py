from fastapi import APIRouter, Depends

from app.api.user.dependencies import get_current_active_auth_user
from app.api.user.schemas import UserRead
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings

from .dao import BookingDAO
from .schemas import (
    BookingCreate,
    BookingFilter,
)

router = APIRouter(
    tags=["Bookings"],
    prefix=settings.api_v1.booking_prefix,
)


@router.get("")
async def get_bookings(
    current_user: UserRead = Depends(get_current_active_auth_user),
    session=SessionDep,
):
    return await BookingDAO.get_all(
        session=session,
        filters=BookingFilter(
            user_id=current_user.id,
        ),
    )


@router.post("")
async def create_booking(
    booking_create_data: BookingCreate,
    current_user: UserRead = Depends(get_current_active_auth_user),
    session=TransactionSessionDep,
):
    return await BookingDAO.create_booking(
        session=session,
        booking_data=booking_create_data,
        user_id=current_user.id,
    )


@router.delete("/{booking_id}")
async def delete_booking(
    booking_id: int,
    current_user: UserRead = Depends(get_current_active_auth_user),
    session=TransactionSessionDep,
):
    return await BookingDAO.delete(
        session=session,
        filters=BookingFilter(
            id=booking_id,
            user_id=current_user.id,
        ),
    )
