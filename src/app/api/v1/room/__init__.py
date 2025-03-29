from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel
from app.api.dependencies.partner import valid_hotel_admin
from app.api.dependencies.room import validate_hotel_room
from app.core import SessionDep, TransactionSessionDep

# from app.core.config import settings
from app.core.exceptions.http_exceptions import (
    NotFoundException,
)
from app.core.utils.parse_date import parse_date
from app.dao.room import RoomDAO
from app.dao.room.types import RoomTypeDAO
from app.schemas.hotel.info import HotelNameRead
from app.schemas.room import (
    RoomCreate,
    RoomCreateInternal,
    RoomFilter,
    RoomRead,
    RoomUpdate,
    RoomUpdateInternal,
)
from app.schemas.room.types import RoomTypeFilter

from .amenities import router as amenities_router
from .images import router as images_router
from .price import router as price_router

# from .types import router as types_router

router = APIRouter(
    tags=["Hotel Rooms"],
    prefix="/hotels",
)


@router.get("/{hotel_id}/rooms")
async def get_hotel_rooms(
    hotel_id: int,
    hotel: HotelNameRead = Depends(validate_hotel),
    session=SessionDep,
):
    return await RoomDAO.get_all(
        session=session,
        filters=RoomFilter(
            hotel_id=hotel_id,
        ),
    )


@router.get("/{hotel_id}/rooms/types")
async def get_hotel_room_types(
    hotel_id: int,
    hotel: HotelNameRead = Depends(validate_hotel),
    session=SessionDep,
):
    return await RoomDAO.get_hotel_room_types(
        session=session,
        hotel_id=hotel_id,
    )


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_room(
    hotel_id: int,
    room_id: int,
    hotel: HotelNameRead = Depends(validate_hotel),
    session=SessionDep,
):
    return await RoomDAO.get_one_or_none(
        session=session,
        filters=RoomFilter(
            hotel_id=hotel_id,
            id=room_id,
        ),
    )


@router.post("/{hotel_id}/rooms")
async def add_hotel_room(
    hotel_id: int,
    hotel_room_data: RoomCreate,
    hotel: HotelNameRead = Depends(valid_hotel_admin),
    session=TransactionSessionDep,
):
    return await RoomDAO.add_room_to_hotel(
        session=session,
        room_data=hotel_room_data,
        hotel_id=hotel_id,
    )


@router.put("/{hotel_id}/rooms/{room_id}")
async def update_hotel_room(
    hotel_id: int,
    room_id: int,
    room_update_data: RoomUpdate,
    room: RoomRead = Depends(validate_hotel),
    session=TransactionSessionDep,
):
    return await RoomDAO.update_hotel_room(
        session=session,
        room_data=room_update_data,
        room_id=room_id,
        hotel_id=hotel_id,
    )


router.include_router(amenities_router)
router.include_router(images_router)
router.include_router(price_router)
