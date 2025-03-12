from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel_room_id
from app.core import SessionDep
from app.dao.room.amenities import (
    RoomAmenityDAO,
)
from app.schemas.room import RoomRead

router = APIRouter(
    tags=["Hotel Room Amenities"],
)


@router.get("/{hotel_id}/rooms/{room_id}/amenities")
async def get_room_amenities(
    room: RoomRead = Depends(validate_hotel_room_id),
    session=SessionDep,
):
    """
    Все удобства комнат
    """
    return await RoomAmenityDAO.get_room__amenities(
        session=session,
        room_id=room.id,
    )
