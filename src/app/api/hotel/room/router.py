from fastapi import APIRouter

# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings

from ..dao import RoomDAO, RoomTypeDAO
from .schemas import (
    RoomCreate,
    RoomFilter,
    RoomTypeCreate,
    RoomUpdate,
)

router = APIRouter(
    prefix=settings.api_v1.room_prefix,
)


@router.get("/")
async def get_all_rooms(
    session=SessionDep,
):
    return await RoomDAO.get_all(
        session=session,
        filters=None,
    )


@router.get("/{room_id}/")
async def get_room(
    room_id: int,
    session=SessionDep,
):
    return await RoomDAO.get_one_or_none_by_id(
        session=session,
        data_id=room_id,
    )


@router.post("/")
async def create_room(
    room_create_data: RoomCreate,
    session=TransactionSessionDep,
):
    return await RoomDAO.create(
        session=session,
        values=room_create_data,
    )


@router.put("/{room_id}/")
async def update_room(
    room_update_data: RoomUpdate,
    room_id: int,
    session=TransactionSessionDep,
):
    return await RoomDAO.update(
        session=session,
        values=room_update_data,
        filters=RoomFilter(
            id=room_id,
        ),
    )


@router.get("/types/")
async def get_room_types(
    session=SessionDep,
):
    return await RoomTypeDAO.get_all(
        session=session,
        filters=None,
    )


@router.post("/types/")
async def create_room_type(
    room_type_create_data: RoomTypeCreate,
    session=TransactionSessionDep,
):
    return await RoomTypeDAO.create(
        session=session,
        values=room_type_create_data,
    )
