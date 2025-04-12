from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel_by_slug
from app.api.dependencies.partner import valid_hotel_admin_by_slug
from app.api.dependencies.room import validate_hotel_room_by_slug
from app.core import SessionDep, TransactionSessionDep
from app.core.exceptions.http_exceptions import (
    NotFoundException,
)
from app.core.i18n.responses import (
    RESPONSE_MESSAGES,
    DataResponse,
)
from app.dao.room.bed import BedTypeDAO, RoomBedConfDAO
from app.schemas.hotel.info import HotelNameRead
from app.schemas.room import RoomRead
from app.schemas.room.bed import (
    BedFilter,
    RoomBedConfCreate,
    RoomBedConfCreateInternal,
    RoomBedConfFilter,
    RoomBedConfRead,
)

router = APIRouter(
    tags=["Hotel Room Beds"],
    prefix="/hotels",
)


@router.get(
    "/{hotel_slug}/rooms/{room_id}/beds",
)
async def get_room_beds(
    hotel_slug: str,
    room_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    session=SessionDep,
):
    return await RoomBedConfDAO.get_all(
        session=session,
        filters=RoomBedConfFilter(
            room_id=room_id,
        ),
    )


@router.post(
    "/{hotel_slug}/rooms/{room_id}/beds",
    response_model=DataResponse[RoomBedConfRead],
)
async def add_room_beds(
    hotel_slug: str,
    room_id: int,
    room_bed_conf: RoomBedConfCreate,
    hotel: HotelNameRead = Depends(valid_hotel_admin_by_slug),
    room: RoomRead = Depends(validate_hotel_room_by_slug),
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
            room_id=room.id,
            **bed_conf.model_dump(),
        )
        await RoomBedConfDAO.create(
            session=session,
            values=bed_conf_create_data,
        )
    return DataResponse(
        data=room_bed_conf,
        message=RESPONSE_MESSAGES.get(
            "DATA_CREATED",
            "Beds added successfully",
        ),
    )
