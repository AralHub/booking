from fastapi import APIRouter

from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings

from .dao import BookingDAO
from .schemas import (
    BookingCreate,
    BookingFilter,
    BookingUpdate,
)

router = APIRouter(
    tags=["Bookings"],
    prefix=settings.api_v1.booking_prefix,
)


@router.get("")
async def get_bookings(
    session=SessionDep,
):
    return await BookingDAO.get_all(
        session=session,
        filters=None,
    )


@router.get("/{booking_id}")
async def get_booking(
    booking_id: int,
    session=SessionDep,
):
    return await BookingDAO.get_one_or_none_by_id(
        session=session,
        data_id=booking_id,
    )


@router.post("")
async def create_booking(
    booking_create_data: BookingCreate,
    session=TransactionSessionDep,
):
    return await BookingDAO.create(
        session=session,
        values=booking_create_data,
    )


@router.put("/{booking_id}")
async def update_booking(
    booking_update_data: BookingUpdate,
    booking_id: int,
    session=TransactionSessionDep,
):
    return await BookingDAO.update(
        session=session,
        values=booking_update_data,
        filters=BookingFilter(
            id=booking_id,
        ),
    )


@router.delete("/{booking_id}")
async def delete_booking(
    booking_id: int,
    session=TransactionSessionDep,
):
    return await BookingDAO.delete(
        session=session,
        filters=BookingFilter(id=booking_id),
    )
