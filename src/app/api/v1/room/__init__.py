from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel_id
from app.core import SessionDep, TransactionSessionDep
from app.core.exceptions.http_exceptions import (
    NotFoundException,
)
from app.dao.room import RoomDAO
from app.dao.room.bed import BedTypeDAO, RoomBedConfDAO
from app.dao.room.types import RoomTypeDAO
from app.schemas.hotel import HotelNameBase
from app.schemas.room import (
    BedFilter,
    RoomBedConfCreate,
    RoomBedConfCreateInternal,
    RoomBedConfFilter,
    RoomCreate,
    RoomCreateInternal,
    RoomFilter,
    RoomTypeCreate,
    RoomTypeFilter,
    RoomUpdate,
    RoomUpdateInternal,
)

router = APIRouter(
    tags=["Rooms"],
)


# region Rooms
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


# endregion
# region Room Beds


@router.get("/{hotel_id}/rooms/{room_id}/beds")
async def get_room_beds(
    hotel_id: int,
    room_id: int,
    session=SessionDep,
):
    return await RoomBedConfDAO.get_all(
        session=session,
        filters=RoomBedConfFilter(
            room_id=room_id,
        ),
    )


@router.post("/{hotel_id}/rooms/{room_id}/beds")
async def add_room_beds(
    hotel_id: int,
    room_id: int,
    room_bed_conf: RoomBedConfCreate,
    session=TransactionSessionDep,
):

    for bed_conf in room_bed_conf.bed_configurations:
        bed_type = await BedTypeDAO.get_one_or_none(
            session=session,
            filters=BedFilter(id=bed_conf.bed_type_id),
        )
        if not bed_type:
            raise NotFoundException(f"Bed type {bed_conf.bed_type_id} not found")
        bed_conf_create_data = RoomBedConfCreateInternal(
            room_id=room_id,
            **bed_conf.model_dump(),
        )
        print(bed_conf_create_data)
        await RoomBedConfDAO.create(
            session=session,
            values=bed_conf_create_data,
        )
    return {
        "message": "Beds added successfully",
    }


# endregion


# region Room Type


@router.get("/rooms/types")
async def get_room_types(
    session=SessionDep,
):
    return await RoomTypeDAO.get_all(
        session=session,
        filters=None,
    )


@router.post("/rooms/types")
async def create_room_type(
    room_type_create_data: RoomTypeCreate,
    session=TransactionSessionDep,
):
    return await RoomTypeDAO.create(
        session=session,
        values=room_type_create_data,
    )


# endregion
