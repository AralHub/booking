from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel_by_slug
from app.api.dependencies.user import get_current_active_auth_user
from app.core import SessionDep, TransactionSessionDep
from app.core.utils import redis_booking
from app.dao.booking import BookingDAO
from app.models.booking import BookingStatus, BookingType
from app.schemas.booking import (
    BookingCreateMultipleRooms,
    BookingFilter,
    BookingInitialCreate,
    BookingUpdateInternal,
)
from app.schemas.hotel.info import HotelNameRead
from app.schemas.user import UserRead

router = APIRouter(
    tags=["Bookings"],
    prefix="",
)


@router.get("/bookings")
async def get_bookings(
    current_user: UserRead = Depends(get_current_active_auth_user),
    session=SessionDep,
):
    bookings = await BookingDAO.get_bookings_by_user_id(
        session=session,
        user_id=current_user.id,
    )
    return {
        "data": bookings,
        "total": len(bookings),
    }


@router.get("/booking/{booking_uuid}")
async def get_initial_booking(booking_uuid: str):
    initial_booking = await redis_booking.get_booking_data(booking_uuid)
    return {
        "data": initial_booking,
    }


@router.post("/hotels/{hotel_slug}/bookings/initial")
async def create_booking_initial(
    hotel_slug: str,
    booking_create_data: BookingInitialCreate,
    current_user: UserRead = Depends(get_current_active_auth_user),
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    session=TransactionSessionDep,
):
    booking_data = await BookingDAO.prepare_booking_data_for_redis(
        session=session,
        booking_data=booking_create_data,
        user_id=current_user.id,
        hotel_id=hotel.id,
    )

    booking_id = await BookingDAO.create_booking_in_redis(
        booking_data=booking_data,
    )

    return {
        "data": {
            "initial_booking_uuid": booking_id,
        }
    }


@router.post("/hotels/{hotel_slug}/bookings/final")
async def create_booking(
    hotel_slug: str,
    booking_create_data: BookingCreateMultipleRooms,
    current_user: UserRead = Depends(get_current_active_auth_user),
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    session=TransactionSessionDep,
):
    booking_type = (
        BookingType.PERSONAL
        if current_user.role == BookingType.PERSONAL
        else BookingType.BUSINESS
    )
    return await BookingDAO.create_booking(
        session=session,
        booking_data=booking_create_data,
        user_id=current_user.id,
        hotel_id=hotel.id,
        booking_type=booking_type,
    )


@router.put("/bookings/{booking_id}/cancel")
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
