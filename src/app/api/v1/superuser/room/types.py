from fastapi import APIRouter

from app.core import SessionDep, TransactionSessionDep
from app.dao.room.types import RoomTypeDAO
from app.schemas.room import (
    RoomTypeCreate,
)

router = APIRouter(
    tags=["Room Types"],
    prefix="/room-types",
)


@router.get("/")
async def get_room_types(
    session=SessionDep,
):
    return await RoomTypeDAO.get_all(
        session=session,
        filters=None,
    )


@router.post("/")
async def create_room_type(
    room_type_create_data: RoomTypeCreate,
    session=TransactionSessionDep,
):
    return await RoomTypeDAO.create(
        session=session,
        values=room_type_create_data,
    )
