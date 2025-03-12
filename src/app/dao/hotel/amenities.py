from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions.http_exceptions import BadRequestException
from app.dao import BaseDAO
from app.models.hotel import Hotel
from app.models.hotel.amenities import (
    HotelAmenity,
    HotelAmenityCategory,
    HotelAmenityAssociation,
)


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

    @classmethod
    async def get_hotel_amenities(
        cls,
        session: AsyncSession,
        hotel_id: int,
    ):
        hotel_amenities = (
            select(Hotel)
            .where(Hotel.id == hotel_id)
            .options(selectinload(Hotel.hotel_amenities))
        )
        result = await session.execute(hotel_amenities)
        return result.scalars().all()

    @classmethod
    async def add_amenities_to_hotel(
        cls,
        session: AsyncSession,
        hotel_id: int,
        amenities: list[int],
    ):
        db_hotel = await session.scalar(
            select(Hotel)
            .where(Hotel.id == hotel_id)
            .options(selectinload(Hotel.hotel_amenities))
        )
        try:
            db_hotel.hotel_amenities.extend(amenities)
            await session.commit()
            return db_hotel
        except IntegrityError as e:
            await session.rollback()
            if "uq_product_extra_product" in str(e):
                raise BadRequestException(
                    "This amenity is already added to the hotel",
                )
            raise BadRequestException(
                "Unable to add amenity to hotel due to database constraint",
            )

    @classmethod
    async def remove_all_amenities_from_hotel(
        cls,
        session: AsyncSession,
        hotel_id: int,
    ):
        hotel = await session.scalar(
            select(Hotel)
            .where(Hotel.id == hotel_id)
            .options(selectinload(Hotel.hotel_amenities))
        )

        await session.execute(
            delete(HotelAmenityAssociation).where(
                HotelAmenityAssociation.hotel_id == hotel_id
            )
        )
        await session.commit()


class HotelAmenityCategoryDAO(BaseDAO):
    model = HotelAmenityCategory
