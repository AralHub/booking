from fastapi import APIRouter

from app.core import SessionDep

router = APIRouter(
    tags=["Room Amenities"],
)


@router.get("/{hotel_id}/rooms/{room_id}/amenities")
async def get_room_amenities(
    hotel_id: int,
    room_id: int,
    session=SessionDep,
):
    return {"message": "Amenities retrieved successfully"}
