from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel_by_slug
from app.api.dependencies.partner import valid_hotel_admin_by_slug
from app.core import SessionDep, TransactionSessionDep
from app.dao.hotel.chessboard import ChessBoardDAO
from app.schemas.hotel.chessboard import (
    ChessBoardCreate,
    ChessBoardFilter,
    ChessBoardUpdateInternal,
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


@router.post("/{hotel_slug}/rooms/room_id/chessboard")
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
