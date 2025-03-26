from fastapi import APIRouter, Depends

from app.api.dependencies.user import get_current_superuser
from app.core import SessionDep, TransactionSessionDep
from app.dao.room.types import RoomTypeDAO
from app.schemas.room.types import (
    RoomTypeCreate,
    RoomTypeFilter,
    RoomTypeUpdate,
)

router = APIRouter(
    tags=["Superuser Room Types"],
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
    room_type_create: RoomTypeCreate,
    session=SessionDep,
):
    return await RoomTypeDAO.create(
        session=session,
        values=room_type_create,
    )


@router.put(
    "/{room_type_id}",
    dependencies=[Depends(get_current_superuser)],
)
async def update_room_type(
    room_type_id: int,
    room_type_update_data: RoomTypeUpdate,
    session=TransactionSessionDep,
):
    return await RoomTypeDAO.update(
        session=session,
        filters=RoomTypeFilter(id=room_type_id),
        values=room_type_update_data,
    )


@router.delete("/{room_type_id}")
async def delete_room_type(
    room_type_id: int,
    session=TransactionSessionDep,
):
    return await RoomTypeDAO.delete(
        session=session, filters=RoomTypeFilter(id=room_type_id)
    )
