from datetime import date

from fastapi import APIRouter
from sqlalchemy.future import select

from app.core import SessionDep
from app.models.hotel.chessboard import ChessBoard

router = APIRouter(prefix="/chessboard")


@router.get("/room-types/{room_type_id}/availability")
async def get_room_availability(
    room_type_id: int,
    start_date: date,
    end_date: date,
    session=SessionDep,
):
    result = await session.execute(
        select(ChessBoard)
        .where(
            ChessBoard.room_type_variant_id == room_type_id,
            ChessBoard.check_date >= start_date,
            ChessBoard.check_date <= end_date,
        )
        .order_by(ChessBoard.check_date)
    )
    availabilities = result.scalars().all()
    return availabilities


@router.put("/room-types/{room_type_id}/availability/{check_date}")
async def update_room_availability(
    room_type_id: int,
    check_date: date,
    availability_data: dict,
    session=SessionDep,
):
    pass
