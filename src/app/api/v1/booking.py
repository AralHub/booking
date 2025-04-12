from fastapi import APIRouter, Depends

from app.api.dependencies.user import get_current_active_auth_user
from app.api.dependencies.hotel import validate_hotel_by_slug
from app.core import SessionDep, TransactionSessionDep
from app.dao.booking import BookingDAO
from app.models.booking import BookingStatus
from app.schemas.booking import (
    BookingCreateMultipleRooms,
    BookingFilter,
    BookingUpdateInternal,
)
from app.schemas.user import UserRead
from app.schemas.hotel.info import HotelNameRead

router = APIRouter(
    tags=["Bookings"],
    prefix="/bookings",
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


@router.post("/{hotel_slug}")
async def create_booking(
    hotel_slug: str,
    booking_create_data: BookingCreateMultipleRooms,
    current_user: UserRead = Depends(get_current_active_auth_user),
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    session=TransactionSessionDep,
):
    return await BookingDAO.create_booking(
        session=session,
        booking_data=booking_create_data,
        user_id=current_user.id,
        hotel_id=hotel.id,
    )


@router.put("/{booking_id}/cancel")
async def cancel_booking(
    booking_id: int,
    current_user: UserRead = Depends(get_current_active_auth_user),
    session=TransactionSessionDep,
):
    return await BookingDAO.update(
        session=session,
        filters=BookingFilter(
            id=booking_id,
            user_id=current_user.id,
        ),
        update_data=BookingUpdateInternal(
            status=BookingStatus.CANCELLED,
        ),
    )
