from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dao import BaseDAO

from .models import (
    RoomAmenity,
    RoomAmenityCategory,
)


class RoomAmenityCategoryDAO(BaseDAO):
    model = RoomAmenityCategory


class RoomAmenityDAO(BaseDAO):
    model = RoomAmenity

    @classmethod
    async def get_all_amenities(
        cls,
        session: AsyncSession,
    ):
        query = select(RoomAmenityCategory).options(
            selectinload(RoomAmenityCategory.room_amenities)
        )
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def add_amenities_to_room(
        cls,
        session: AsyncSession,
        room_id: int,
        room_amenities_list: list[int],
    ):
        pass
