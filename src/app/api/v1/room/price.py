from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel_by_slug
from app.api.dependencies.partner import valid_hotel_admin_by_slug
from app.api.dependencies.room import validate_hotel_room_by_slug
from app.core import SessionDep, TransactionSessionDep
from app.core.exceptions.http_exceptions import BadRequestException
from app.core.i18n.responses import RESPONSE_MESSAGES, DataResponse, ListResponse
from app.core.i18n.translations import ErrorCode
from app.dao.room import RoomDAO
from app.dao.room.price import RoomPriceDAO
from app.schemas.hotel.info import HotelNameRead
from app.schemas.room import RoomFilter, RoomRead, RoomUpdateInternal
from app.schemas.room.price import (
    RoomPriceCreate,
    RoomPriceCreateInternal,
    RoomPriceRead,
)

router = APIRouter(
    tags=["Hotel Room Prices"],
)


@router.get(
    "/{hotel_slug}/rooms/{room_id}/prices",
    response_model=ListResponse[RoomPriceRead],
)
async def get_room_prices(
    hotel_slug: str,
    room_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    room: RoomRead = Depends(validate_hotel_room_by_slug),
    session=SessionDep,
):
    room_prices = await RoomPriceDAO.get_room_prices(
        session=session,
        room_id=room.id,
    )
    return ListResponse(
        data=[RoomPriceRead.model_validate(room_price) for room_price in room_prices],
        total=len(room_prices),
    )


@router.post(
    "/{hotel_slug}/rooms/{room_id}/prices",
    response_model=DataResponse[RoomPriceRead],
)
async def create_room_price(
    hotel_slug: str,
    room_id: int,
    room_price_data: RoomPriceCreate,
    hotel: HotelNameRead = Depends(valid_hotel_admin_by_slug),
    room: RoomRead = Depends(validate_hotel_room_by_slug),
    session=TransactionSessionDep,
):
    if room_price_data.guest_quantity > room.max_guests:
        raise BadRequestException(
            error_code=ErrorCode.BAD_REQUEST,
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
    return DataResponse(
        data=created_room_price,
        message=RESPONSE_MESSAGES.get(
            "DATA_CREATED",
            "Room price created successfully",
        ),
    )
