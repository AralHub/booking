from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dao import BaseDAO

from app.models.room.amenities import (
    RoomAmenity,
    RoomAmenityCategory,
)


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
    async def get_room_amenities(cls, session: AsyncSession, room_id: int):
        query = select(cls.model).filter_by(room_id=room_id)
        result = await session.execute(query)
        return result.scalars().all()
