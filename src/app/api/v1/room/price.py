from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import valid_hotel_admin, validate_hotel_room_id
from app.core import SessionDep, TransactionSessionDep
from app.dao.room.price import RoomPriceDAO
from app.schemas.hotel.info import HotelNameRead
from app.schemas.room import RoomRead
from app.schemas.room.price import (
    RoomPriceCreate,
    RoomPriceCreateInternal,
    RoomPriceFilter,
    RoomPriceUpdate,
)

router = APIRouter(
    tags=["Hotel Room Prices"],
)


@router.get("/{hotel_id}/rooms/{room_id}/prices")
async def get_room_price(
    hotel_id: int,
    room_id: int,
    hotel_room: RoomRead = Depends(validate_hotel_room_id),
    session=SessionDep,
):
    return await RoomPriceDAO.get_one_or_none(
        session=session,
        filters=RoomPriceFilter(
            room_id=room_id,
        ),
    )


@router.post("/{hotel_id}/rooms/{room_id}/prices")
async def create_room_price(
    hotel_id: int,
    room_id: int,
    room_price_data: RoomPriceCreate,
    hotel_room: RoomRead = Depends(validate_hotel_room_id),
    hotel: HotelNameRead = Depends(valid_hotel_admin),
    session=TransactionSessionDep,
):
    room_price_create_data = RoomPriceCreateInternal(
        room_id=room_id,
        **room_price_data.model_dump(
            exclude_unset=True,
        ),
    )
    created_room_price = await RoomPriceDAO.create(
        session=session,
        values=room_price_create_data,
    )
    return created_room_price
