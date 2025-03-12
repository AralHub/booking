from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import valid_hotel_admin, validate_hotel_id
from app.core import SessionDep, TransactionSessionDep
from app.core.exceptions.http_exceptions import (
    NotFoundException,
)
from app.dao.room.bed import BedTypeDAO, RoomBedConfDAO
from app.schemas.hotel.info import HotelNameRead
from app.schemas.room import (
    BedFilter,
    RoomBedConfCreate,
    RoomBedConfCreateInternal,
    RoomBedConfFilter,
)

router = APIRouter(
    tags=["Room Beds"],
)


@router.get("/{hotel_id}/rooms/{room_id}/beds")
async def get_room_beds(
    hotel_id: int,
    room_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_id),
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
    hotel: HotelNameRead = Depends(valid_hotel_admin),
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
