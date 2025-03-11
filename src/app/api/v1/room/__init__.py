from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel_id
from app.core import SessionDep, TransactionSessionDep
from app.core.exceptions.http_exceptions import (
    NotFoundException,
)
from app.dao.room import RoomDAO
from app.dao.room.types import RoomTypeDAO
from app.schemas.hotel import HotelNameBase
from app.schemas.room import (
    RoomCreate,
    RoomCreateInternal,
    RoomFilter,
    RoomTypeFilter,
    RoomUpdate,
    RoomUpdateInternal,
)

router = APIRouter(
    tags=["Rooms"],
)


@router.get("/hotels/{hotel_id}/rooms")
async def get_all_rooms(
    hotel_id: int,
    session=SessionDep,
):
    return await RoomDAO.get_all(
        session=session,
        filters=RoomFilter(
            hotel_id=hotel_id,
        ),
    )


@router.get("/hotels/{hotel_id}/rooms/types")
async def get_room_categories(
    hotel_id: int,
    session=SessionDep,
):
    return await RoomDAO.get_hotel_room_types(
        session=session,
        hotel_id=hotel_id,
    )


@router.get("/hotels/{hotel_id}/rooms/{room_id}")
async def get_room(
    hotel_id: int,
    room_id: int,
    session=SessionDep,
):
    return await RoomDAO.get_one_or_none(
        session=session,
        filters=RoomFilter(
            hotel_id=hotel_id,
            id=room_id,
        ),
    )


@router.post("/hotels/{hotel_id}/rooms")
async def add_room(
    hotel_id: int,
    hotel_room_data: RoomCreate,
    session=TransactionSessionDep,
):
    db_room_type = await RoomTypeDAO.get_one_or_none(
        session=session,
        filters=RoomTypeFilter(
            id=hotel_room_data.room_type_id,
        ),
    )
    if not db_room_type:
        raise NotFoundException("Room type not found")
    hotel_room_create_data = RoomCreateInternal(
        **hotel_room_data.model_dump(),
        hotel_id=hotel_id,
    )
    await RoomDAO.create(
        session=session,
        values=hotel_room_create_data,
    )


@router.put("/hotels/{hotel_id}/rooms/{room_id}")
async def update_room(
    hotel_id: int,
    room_id: int,
    room_update_data: RoomUpdate,
    hotel: HotelNameBase = Depends(validate_hotel_id),
    session=TransactionSessionDep,
):
    updated_row_count = await RoomDAO.update(
        session=session,
        values=RoomUpdateInternal(
            **room_update_data.model_dump(
                exclude_none=True,
            )
        ),
        filters=RoomFilter(
            id=room_id,
            hotel_id=hotel_id,
        ),
    )
    if updated_row_count == 0:
        raise NotFoundException("Room not found")
    return {
        "message": "Room updated successfully",
    }
