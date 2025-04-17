from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.exceptions.http_exceptions import (
    NotFoundException,
    BadRequestException,
)
from app.dao import BaseDAO
from app.models.room import Room
from app.models.room.types import RoomType
from app.schemas.room import (
    RoomCreateInternal,
    RoomCreate,
    RoomUpdate,
    RoomUpdateInternal,
    RoomFilter,
    RoomRead,
)
from app.schemas.room.types import RoomTypeFilter
from app.dao.room.amenities import RoomAmenityDAO
import logging

logger = logging.getLogger(__name__)


class RoomTypeDAO(BaseDAO):
    model = RoomType


class RoomDAO(BaseDAO):
    model = Room

    @classmethod
    async def add_room_to_hotel(
        cls,
        session: AsyncSession,
        room_data: RoomCreate,
        hotel_id: int,
    ):
        db_room_type = await RoomTypeDAO.get_one_or_none(
            session=session,
            filters=RoomTypeFilter(
                id=room_data.room_type_id,
            ),
        )
        if not db_room_type:
            raise NotFoundException(
                detail="Room type not found",
            )
        hotel_room_create_data = RoomCreateInternal(
            **room_data.model_dump(
                exclude={
                    "amenities",
                }
            ),
            hotel_id=hotel_id,
        )
        created_room = await cls.create(
            session=session,
            values=hotel_room_create_data,
        )
        if room_data.amenities and len(room_data.amenities) != 0:
            await RoomAmenityDAO.delete_room_all_amenities(
                session=session,
                room_id=created_room.id,
            )
            await RoomAmenityDAO.add_amenities_to_room(
                session=session,
                room_id=created_room.id,
                amenities=room_data.amenities,
            )
        return created_room

    @classmethod
    async def update_hotel_room(
        cls,
        session: AsyncSession,
        room_data: RoomUpdate,
        room_id: int,
        hotel_id: int,
        amenities: list[int] | None = None,
    ):
        # Проверяем существование room_type если он указан
        if room_data.room_type_id is not None:
            room_type = await RoomTypeDAO.get_one_or_none(
                session=session,
                filters=RoomTypeFilter(
                    id=room_data.room_type_id,
                ),
            )
            if not room_type:
                raise NotFoundException("Room type does not exist")
        updated_room = await RoomDAO.update(
            session=session,
            values=RoomUpdateInternal(
                **room_data.model_dump(
                    exclude_none=True,
                    exclude_unset=True,
                    exclude={"amenities"},
                )
            ),
            filters=RoomFilter(
                id=room_id,
                hotel_id=hotel_id,
            ),
        )
        if amenities and len(amenities) != 0:
            await RoomAmenityDAO.delete_room_all_amenities(
                session=session,
                room_id=room_id,
            )
            await RoomAmenityDAO.add_amenities_to_room(
                session=session,
                room_id=room_id,
                amenities=amenities,
            )
        return updated_room

    @classmethod
    async def get_hotel_rooms(
        cls,
        session: AsyncSession,
        hotel_id: int,
    ):
        query = (
            select(cls.model)
            .options(
                selectinload(cls.model.room_type),
                selectinload(cls.model.room_images),
            )
            .where(cls.model.hotel_id == hotel_id)
        )

        result = await session.execute(query)
        # Получаем список Room объектов
        data = result.scalars().unique().all()

        rooms = []
        for row in data:
            room_dict = {
                "id": row.id,
                "quantity": row.quantity,
                "base_price": row.base_price,
                "room_area": row.room_area,
                "hotel_id": row.hotel_id,
                "max_guests": row.max_guests,
                "room_type_id": row.room_type_id,
                "use_dinamic_price": row.use_dinamic_price,
                "room_type": row.room_type.name,
                "images": row.room_images,
            }
            rooms.append(room_dict)

        return rooms

    @classmethod
    async def get_hotel_room_by_id(
        cls,
        session: AsyncSession,
        room_id: int,
    ):
        query = (
            select(cls.model)
            .options(
                selectinload(cls.model.room_type),
                selectinload(cls.model.room_images),
            )
            .where(cls.model.id == room_id)
        )
        result = await session.execute(query)
        room = result.scalars().unique().one_or_none()
        if not room:
            return None

        room_dict = {
            "id": room.id,
            "quantity": room.quantity,
            "base_price": room.base_price,
            "room_area": room.room_area,
            "hotel_id": room.hotel_id,
            "max_guests": room.max_guests,
            "use_dinamic_price": room.use_dinamic_price,
            "room_type_id": room.room_type_id,
            "room_type": room.room_type.name,
            "images": room.room_images,
        }
        return room_dict
