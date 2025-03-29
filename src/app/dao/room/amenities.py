from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from app.dao import BaseDAO
from app.core.exceptions.http_exceptions import BadRequestException
from app.models.room.amenities import (
    RoomAmenity,
    RoomAmenityCategory,
)
from app.models.room import Room


class RoomAmenityCategoryDAO(BaseDAO):
    model = RoomAmenityCategory

    @classmethod
    async def get_all_amenities(
        cls,
        session: AsyncSession,
    ):
        query = select(cls.model).options(selectinload(cls.model.room_amenities))
        result = await session.execute(query)
        return result.scalars().all()


class RoomAmenityDAO(BaseDAO):
    model = RoomAmenity

    @classmethod
    async def get_room_amenities(
        cls,
        session: AsyncSession,
        room_id: int,
    ):
        query = select(cls.model).filter_by(room_id=room_id)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def add_amenities_to_room(
        cls,
        session: AsyncSession,
        room_id: int,
        amenities: list[int],
    ):
        query = (
            select(Room)
            .options(selectinload(Room.room_amenities))
            .where(Room.id == room_id)
        )
        result = await session.execute(query)
        db_room = result.scalar_one_or_none()
        for room_amenity_id in amenities:
            room_amenity = await cls.get_one_or_none_by_id(
                session=session,
                data_id=room_amenity_id,
            )
            if room_amenity:
                db_room.room_amenities.append(room_amenity)
        await session.commit()
