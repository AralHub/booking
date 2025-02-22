from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dao import BaseDAO

from .models import HotelAmenity, HotelAmenityCategory


class HotelAmenityDAO(BaseDAO):
    model = HotelAmenity

    @classmethod
    async def get_all_amenities(
        cls,
        session: AsyncSession,
    ):
        query = (
            select(HotelAmenityCategory)
            .join(cls.model)
            .where(HotelAmenityCategory.id == cls.model.hotel_amenity_category_id)
        )
        print(
            "Generated SQL:", str(query)
        )  # This will show us the actual SQL being generated
        result = await session.execute(query)
        data = result.scalars().all()
        print(
            "Result data structure:", type(data)
        )  # This will show us the type of data returned
        print(
            "First item structure:", type(data[0]) if data else None
        )  # This will show us the structure of individual items
        return data


class HotelAmenityCategoryDAO(BaseDAO):
    model = HotelAmenityCategory
