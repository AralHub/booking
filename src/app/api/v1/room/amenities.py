from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel
from app.api.dependencies.partner import valid_hotel_admin
from app.api.dependencies.room import validate_hotel_room
from app.core import SessionDep
from app.dao.room.amenities import RoomAmenityDAO
from app.schemas.hotel.info import HotelNameRead
from app.schemas.room import RoomRead
from app.schemas.room.amenities import RoomAmenityRead, RoomAmenityAssociationRead
from app.core.i18n.responses import (
    ListResponse,
    DataResponse,
    BaseResponse,
    RESPONSE_MESSAGES,
)

router = APIRouter(
    tags=["Hotel Room Amenities"],
)


@router.get(
    "/{hotel_id}/rooms/{room_id}/amenities",
    response_model=DataResponse[RoomAmenityAssociationRead],
)
async def get_room_amenities(
    hotel_id: int,
    room_id: int,
    room: RoomRead = Depends(validate_hotel_room),
    hotel: HotelNameRead = Depends(validate_hotel),
    session=SessionDep,
):
    """
    Все удобства комнат
    """
    room_amenities = await RoomAmenityDAO.get_room_amenities(
        session=session,
        room_id=room_id,
    )
    return DataResponse(
        data=room_amenities,
    )


@router.post("/{hotel_id}/rooms/{room_id}/amenities")
async def add_amenities_to_room(
    hotel_id: int,
    room_id: int,
    amenities: list[int],
    hotel: HotelNameRead = Depends(valid_hotel_admin),
    room: RoomRead = Depends(validate_hotel_room),
    session=SessionDep,
):
    return await RoomAmenityDAO.add_amenities_to_room(
        session=session,
        room_id=room_id,
        room_amenities=amenities,
    )


@router.delete("/{hotel_id}/rooms/{room_id}/amenities")
async def remove_amenities_from_room(
    hotel_id: int,
    room_id: int,
    hotel: HotelNameRead = Depends(valid_hotel_admin),
    session=SessionDep,
):
    return await RoomAmenityDAO.remove_all_amenities_from_room(
        session=session,
        hotel_id=hotel_id,
    )


@router.delete("/{hotel_id}/rooms/{room_id}/amenities/{amenity_id}")
async def remove_amenity_from_room_by_id(
    hotel_id: int,
    room_id: int,
    amenity_id: int,
    hotel: HotelNameRead = Depends(valid_hotel_admin),
    session=SessionDep,
):
    await RoomAmenityDAO.remove_amenity_from_room(
        session=session,
        room_id=room_id,
        amenity_id=amenity_id,
    )
    return {"message": "Amenity removed from room"}
