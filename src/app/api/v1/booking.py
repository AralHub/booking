from fastapi import APIRouter, Depends

from app.api.dependencies.user import get_current_active_auth_user
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings
from app.dao.booking import BookingDAO
from app.models.booking import BookingStatus
from app.schemas.booking import BookingCreate, BookingFilter, BookingUpdateInternal
from app.schemas.user import UserRead

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


@router.put("/{booking_id}")
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
