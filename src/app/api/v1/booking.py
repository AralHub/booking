from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_active_hotel
from app.api.dependencies.user import get_current_active_auth_user
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings
from app.dao.booking import BookingDAO
from app.models.booking import BookingStatus
from app.schemas.booking import (
    BookingCreateMultipleRooms,
    BookingFilter,
    BookingUpdateInternal,
)
from app.schemas.hotel.info import HotelNameRead
from app.schemas.user import UserRead

router = APIRouter(
    tags=["Hotel Boookings"],
    prefix=settings.api_v1.hotel_prefix,
)


@router.get("/{hotel_id}/bookings")
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


@router.post("{hotel_id}/bookings")
async def create_booking(
    hotel_id: int,
    booking_create_data: BookingCreateMultipleRooms,
    hotel: HotelNameRead = Depends(validate_active_hotel),
    current_user: UserRead = Depends(get_current_active_auth_user),
    session=TransactionSessionDep,
):
    return await BookingDAO.create_booking(
        session=session,
        booking_data=booking_create_data,
        user_id=current_user.id,
        hotel_id=hotel_id,
    )


@router.put("/{hotel_id}/bookings/{booking_id}/cancel")
async def cancel_booking(
    booking_id: int,
    hotel: HotelNameRead = Depends(validate_active_hotel),
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
