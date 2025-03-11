from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dao import BaseDAO

from .models import HotelAmenity, HotelAmenityCategory


class HotelAmenityDAO(BaseDAO):
    model = HotelAmenity

    @classmethod
    async def get_all_amenities(
        cls,
        session: AsyncSession,
    ):
        query = select(HotelAmenityCategory).options(
            selectinload(HotelAmenityCategory.hotel_amenities)
        )
        result = await session.execute(query)
        return result.scalars().all()


class HotelAmenityCategoryDAO(BaseDAO):
    model = HotelAmenityCategory
