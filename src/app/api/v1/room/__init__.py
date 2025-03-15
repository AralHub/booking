from fastapi import APIRouter, Depends
from app.core.utils.parse_date import parse_date

from app.api.dependencies.hotel import (
    valid_hotel_admin,
    validate_hotel_id,
    validate_hotel_room_id,
)
from app.core import SessionDep, TransactionSessionDep

# from app.core.config import settings
from app.core.exceptions.http_exceptions import (
    NotFoundException,
)
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
from app.schemas.room.types import RoomTypeFilter

from .amenities import router as amenities_router
from .images import router as images_router
from .price import router as price_router

# from .types import router as types_router

router = APIRouter(
    tags=["Hotel Rooms"],
    prefix="/hotels",
)


@router.get("/rooms/available")
async def get_available_rooms(
    hotel_id: int,
    check_in_date: str,
    check_out_date: str,
    guests_count: int,
    session=SessionDep,
):
    check_in_date = parse_date(check_in_date)
    check_out_date = parse_date(check_out_date)
    return await RoomDAO.get_available_rooms(
        session=session,
        hotel_id=hotel_id,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        guests=guests_count,
    )


@router.get("/{hotel_id}/rooms")
async def get_hotel_rooms(
    hotel_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_id),
    session=SessionDep,
):
    return await RoomDAO.get_all(
        session=session,
        filters=RoomFilter(
            hotel_id=hotel_id,
        ),
    )


@router.get("/{hotel_id}/rooms/types")
async def get_hotel_room_types(
    hotel_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_id),
    session=SessionDep,
):
    return await RoomDAO.get_hotel_room_types(
        session=session,
        hotel_id=hotel_id,
    )


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_room(
    hotel_id: int,
    room_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_id),
    session=SessionDep,
):
    return await RoomDAO.get_one_or_none(
        session=session,
        filters=RoomFilter(
            hotel_id=hotel_id,
            id=room_id,
        ),
    )


@router.post("/{hotel_id}/rooms")
async def add_hotel_room(
    hotel_id: int,
    hotel_room_data: RoomCreate,
    hotel: HotelNameRead = Depends(valid_hotel_admin),
    session=TransactionSessionDep,
):
    db_room_type = await RoomTypeDAO.get_one_or_none(
        session=session,
        filters=RoomTypeFilter(
            id=hotel_room_data.room_type_id,
        ),
    )
    if not db_room_type:
        raise NotFoundException("Room type not found")
    hotel_room_create_data = RoomCreateInternal(
        **hotel_room_data.model_dump(),
        hotel_id=hotel_id,
    )
    await RoomDAO.create(
        session=session,
        values=hotel_room_create_data,
    )


@router.put("/{hotel_id}/rooms/{room_id}")
async def update_hotel_room(
    hotel_id: int,
    room_id: int,
    room_update_data: RoomUpdate,
    room: RoomRead = Depends(validate_hotel_room_id),
    session=TransactionSessionDep,
):
    # Проверяем существование room_type если он указан
    if room_update_data.room_type_id is not None:
        room_type = await RoomTypeDAO.get_one_or_none(
            session=session,
            filters=RoomTypeFilter(
                id=room_update_data.room_type_id,
            ),
        )
        if not room_type:
            raise NotFoundException("Room type does not exist")
    updated_row_count = await RoomDAO.update(
        session=session,
        values=RoomUpdateInternal(
            **room_update_data.model_dump(
                exclude_none=True,
                exclude_unset=True,
            )
        ),
        filters=RoomFilter(
            id=room_id,
            hotel_id=hotel_id,
        ),
    )
    if updated_row_count == 0 or updated_row_count is None:
        raise NotFoundException("Room did not update")
    return {
        "message": "Room updated successfully",
    }


router.include_router(amenities_router)
router.include_router(images_router)
router.include_router(price_router)
