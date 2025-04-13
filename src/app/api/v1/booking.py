import uuid as uuid_pkg

from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel_by_slug
from app.api.dependencies.user import get_current_active_auth_user
from app.core import SessionDep, TransactionSessionDep
from app.core.utils import redis_booking
from app.dao.booking import BookingDAO
from app.models.booking import BookingStatus
from app.schemas.booking import (
    BookingCreateMultipleRooms,
    BookingFilter,
    BookingInitialCreate,
    BookingInitialCreateInternal,
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
    return await BookingDAO.get_all(
        session=session,
        filters=BookingFilter(
            user_id=current_user.id,
        ),
    )


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
    await BookingDAO.check_rooms_availability(
        session=session,
        check_in_date=booking_create_data.check_in_date,
        check_out_date=booking_create_data.check_out_date,
        hotel_id=hotel.id,
        rooms_info=booking_create_data.rooms_info,
    )
    booking_create = BookingInitialCreateInternal(
        uuid=str(uuid_pkg.uuid4()),
        hotel_id=hotel.id,
        user_id=current_user.id,
        **booking_create_data.model_dump(),
    )
    booking_id = await redis_booking.add_booking(booking_create)
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
    return await BookingDAO.create_booking(
        session=session,
        booking_data=booking_create_data,
        user_id=current_user.id,
        hotel_id=hotel.id,
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
