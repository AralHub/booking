from app.core.dao import BaseDAO
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
        query = select(RoomAmenityCategoryDAO).options(
            selectinload(RoomAmenityCategoryDAO.hotel_amenities)
        )
        result = await session.execute(query)
        return result.scalars().all()
