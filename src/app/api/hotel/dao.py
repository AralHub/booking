from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.amenity.hotel_amenity.dao import HotelAmenityDAO
from app.api.hotel.models import Hotel, HotelCategory
from app.core.dao import BaseDAO
from app.core.exceptions.http_exceptions import NotFoundException


class HotelDAO(BaseDAO):
    model = Hotel

    @classmethod
    async def add_hotel_amenities(
        cls,
        hotel_id: int,
        hotel_amenities_data: list[int],
        session: AsyncSession,
    ):
        query = (
            select(Hotel)
            .options(selectinload(Hotel.hotel_amenities))
            .where(Hotel.id == hotel_id)
        )
        result = await session.execute(query)
        db_hotel = result.scalar_one_or_none()
        # db_hotel = await session.scalar(
        #     select(Hotel).where(Hotel.id == hotel_id),
        # )
        if not db_hotel:
            raise NotFoundException("Hotel not found")
        for hotel_amenity_id in hotel_amenities_data:
            hotel_amenity = await HotelAmenityDAO.get_one_or_none_by_id(
                session=session,
                data_id=hotel_amenity_id,
            )
            if hotel_amenity:
                db_hotel.hotel_amenities.append(hotel_amenity)
        await session.commit()


class HotelCategoryDAO(BaseDAO):
    model = HotelCategory
