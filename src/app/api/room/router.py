from fastapi import APIRouter

# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings

from .dao import RoomDAO, RoomTypeDAO
from .schemas import (
    RoomCreate,
    RoomFilter,
    RoomTypeCreate,
    RoomUpdate,
)

router = APIRouter(
    tags=["Rooms"],
    prefix=settings.api_v1.room_prefix,
)


# region Room Type


@router.get("/types")
async def get_room_types(
    session=SessionDep,
):
    return await RoomTypeDAO.get_all(
        session=session,
        filters=None,
    )


@router.post("/types")
async def create_room_type(
    room_type_create_data: RoomTypeCreate,
    session=TransactionSessionDep,
):
    return await RoomTypeDAO.create(
        session=session,
        values=room_type_create_data,
    )


# endregion


# region RoomTypeVariants
@router.get("/types/{room_type_id}/variants")
async def get_room_type_variants(
    room_type_id: int,
    session=SessionDep,
):
    return await RoomTypeDAO.get_room_type_variants(
        room_type_id=room_type_id,
        session=session,
    )


# endregion
