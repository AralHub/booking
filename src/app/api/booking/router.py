from fastapi import APIRouter, Depends

from app.core import SessionDep
from app.core.config import settings
from app.dao import BookingDAO

router = APIRouter(
    tags=["Booking"],
    prefix=settings.api_v1.booking_prefix,
)


@router.get("/")
async def get_booking(
    session=SessionDep,
):
    return await BookingDAO.get_all(
        session=session,
        filters=None,
    )
