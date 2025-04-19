from datetime import datetime

from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel_by_slug
from app.api.dependencies.partner import valid_hotel_admin_by_slug
from app.core import SessionDep, TransactionSessionDep
from app.core.exceptions.http_exceptions import BadRequestException
from app.core.i18n.translations import ErrorCode
from app.dao.booking import BookingDAO
from app.dao.hotel.chessboard import ChessBoardDAO
from app.schemas.hotel.chessboard import (
    ChessBoardCreate,
)
from app.schemas.hotel.info import HotelNameRead
from app.schemas.partner import PartnerRead

router = APIRouter(
    prefix="/hotels",
    tags=["Hotel Chessboard"],
)


@router.get("/{hotel_slug}/chessboard")
async def get_chessboard_items(
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    # partner: PartnerRead = Depends(valid_hotel_admin_by_slug),
    session=SessionDep,
):
    items = await ChessBoardDAO.get_chessboard_items(
        session=session,
        hotel_id=hotel.id,
    )
    return {
        "data": items,
        "total": len(items),
    }


@router.post("/{hotel_slug}/rooms/{room_id}/chessboard")
async def create_chessboard_item(
    room_id: int,
    create_data: ChessBoardCreate,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    partner: PartnerRead = Depends(valid_hotel_admin_by_slug),
    session=TransactionSessionDep,
):
    created_chessboard_item = await ChessBoardDAO.create_chessboard_item(
        session=session,
        room_id=room_id,
        create_data=create_data,
    )
    return created_chessboard_item


@router.get("/{hotel_slug}/chessboard/active-bookings")
async def get_active_bookings(
    start_date: str,
    end_date: str,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    session=SessionDep,
):
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        start_date = start_date.date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        end_date = end_date.date()
    except ValueError:
        raise BadRequestException(
            error_code=ErrorCode.BAD_REQUEST,
            detail="Invalid date format",
        )
    active_booked_rooms_count = await BookingDAO.get_booked_rooms_by_dates(
        session=session,
        start_date=start_date,
        end_date=end_date,
        hotel_id=hotel.id,
    )
    return active_booked_rooms_count
