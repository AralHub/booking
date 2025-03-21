from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import valid_hotel_admin, validate_hotel_room_id
from app.core import SessionDep, TransactionSessionDep
from app.core.exceptions.http_exceptions import BadRequestException
from app.dao.room import RoomDAO
from app.dao.room.price import RoomPriceDAO
from app.schemas.hotel.info import HotelNameRead
from app.schemas.room import RoomFilter, RoomRead, RoomUpdateInternal
from app.schemas.room.price import (
    RoomPriceCreate,
    RoomPriceCreateInternal,
)

router = APIRouter(
    tags=["Hotel Room Prices"],
)


@router.get("/{hotel_id}/rooms/{room_id}/prices")
async def get_room_prices(
    hotel_id: int,
    room_id: int,
    hotel_room: RoomRead = Depends(validate_hotel_room_id),
    session=SessionDep,
):
    return await RoomPriceDAO.get_room_prices(
        session=session,
        room_id=room_id,
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
    if room_price_data.guest_quantity > hotel_room.max_guests:
        raise BadRequestException(
            "Guest quantity cannot be greater than the room's maximum guests",
        )
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
    await RoomDAO.update(
        session=session,
        filters=RoomFilter(id=room_id),
        values=RoomUpdateInternal(
            use_dinamic_price=True,
        ),
    )
    return created_room_price
