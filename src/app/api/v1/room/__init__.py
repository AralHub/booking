from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel_by_slug
from app.api.dependencies.partner import valid_hotel_admin, valid_hotel_admin_by_slug
from app.api.dependencies.room import validate_hotel_room, validate_hotel_room_by_slug
from app.core import SessionDep, TransactionSessionDep

# from app.core.config import settings
from app.core.exceptions.http_exceptions import (
    NotFoundException,
)
from app.core.i18n.responses import (
    RESPONSE_MESSAGES,
    BaseResponse,
    DataResponse,
    ListResponse,
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
from app.schemas.room.types import RoomTypeFilter, RoomTypeRead

# from .types import router as types_router

router = APIRouter(
    tags=["Hotel Rooms"],
    prefix="/hotels",
)


@router.get(
    "/{hotel_slug}/rooms",
    response_model=ListResponse[RoomRead],
)
async def get_hotel_rooms(
    hotel_slug: str,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    session=SessionDep,
):
    rooms = await RoomDAO.get_all(
        session=session,
        filters=RoomFilter(
            hotel_id=hotel.id,
        ),
    )
    return ListResponse(
        data=rooms,
        total=len(rooms),
    )


@router.get(
    "/{hotel_slug}/rooms/types",
    response_model=ListResponse[RoomTypeRead],
)
async def get_hotel_room_types(
    hotel_slug: str,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    session=SessionDep,
):
    room_types = await RoomDAO.get_hotel_room_types(
        session=session,
        hotel_id=hotel.id,
    )
    return ListResponse(
        data=room_types,
        total=len(room_types),
    )


@router.get(
    "/{hotel_slug}/rooms/{room_id}",
    response_model=DataResponse[RoomRead],
)
async def get_room(
    hotel_slug: str,
    room_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    room: RoomRead = Depends(validate_hotel_room_by_slug),
    session=SessionDep,
):
    room = await RoomDAO.get_one_or_none(
        session=session,
        filters=RoomFilter(
            hotel_id=hotel.id,
            id=room_id,
        ),
    )
    return DataResponse(
        data=room,
    )


@router.post(
    "/{hotel_slug}/rooms",
    response_model=DataResponse[RoomRead],
)
async def add_hotel_room(
    hotel_slug: str,
    hotel_room_data: RoomCreate,
    hotel: HotelNameRead = Depends(valid_hotel_admin_by_slug),
    session=TransactionSessionDep,
):
    added_room = await RoomDAO.add_room_to_hotel(
        session=session,
        room_data=hotel_room_data,
        hotel_id=hotel.id,
    )
    return DataResponse(
        data=added_room,
        message=RESPONSE_MESSAGES.get(
            "DATA_CREATED",
            "Room created successfully",
        ),
    )


@router.put(
    "/{hotel_slug}/rooms/{room_id}",
    response_model=DataResponse[RoomRead],
)
async def update_hotel_room(
    hotel_slug: str,
    room_id: int,
    room_update_data: RoomUpdate,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    room: RoomRead = Depends(validate_hotel_room_by_slug),
    session=TransactionSessionDep,
):
    updated_room = await RoomDAO.update_hotel_room(
        session=session,
        room_data=room_update_data,
        room_id=room.id,
        hotel_id=hotel.id,
    )
    return DataResponse(
        data=updated_room,
        message=RESPONSE_MESSAGES.get(
            "DATA_UPDATED",
            "Room updated successfully",
        ),
    )
