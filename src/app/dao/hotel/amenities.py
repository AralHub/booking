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


class HotelAmenityCategoryDAO(BaseDAO):
    model = HotelAmenityCategory

    @classmethod
    async def get_all_amenities(
        cls,
        session: AsyncSession,
    ):
        query = select(cls.model).options(selectinload(cls.model.hotel_amenities))
        result = await session.execute(query)
        return result.scalars().all()


class HotelAmenityDAO(BaseDAO):
    model = HotelAmenity

    @classmethod
    async def get_hotel_amenities(cls, hotel_id: int, session: AsyncSession):
        query = (
            select(Hotel)
            .options(selectinload(Hotel.hotel_amenities))
            .where(Hotel.id == hotel_id)
        )
        result = await session.execute(query)
        db_hotel = result.scalar_one_or_none()

        return db_hotel.hotel_amenities if db_hotel else []

    @classmethod
    async def delete_hotel_all_amenities(
        cls,
        hotel_id: int,
        session: AsyncSession,
    ):
        db_hotel = await session.scalar(
            select(cls.model)
            .where(cls.model.id == hotel_id)
            .options(selectinload(cls.model.hotel_amenities))
        )

        await session.execute(
            delete(HotelAmenityAssociation).where(
                HotelAmenityAssociation.hotel_id == hotel_id
            )
        )
        await session.commit()

    @classmethod
    async def delete_amenity_from_hotel(
        cls,
        session: AsyncSession,
        hotel_id: int,
        amenity_id: int,
    ):
        query = select(HotelAmenityAssociation).where(
            HotelAmenityAssociation.hotel_id == hotel_id,
            HotelAmenityAssociation.hotel_amenity_id == amenity_id,
        )
        result = await session.execute(query)
        amenity_association = result.scalar()
        await session.delete(amenity_association)
        await session.commit()

    @classmethod
    async def add_hotel_amenities(
        cls,
        hotel_id: int,
        amenities: list[int],
        session: AsyncSession,
    ):
        query = (
            select(Hotel)
            .options(selectinload(Hotel.hotel_amenities))
            .where(Hotel.id == hotel_id)
        )
        result = await session.execute(query)
        db_hotel = result.scalar_one_or_none()
        for hotel_amenity_id in amenities:
            hotel_amenity = await HotelAmenityDAO.get_one_or_none_by_id(
                session=session,
                data_id=hotel_amenity_id,
            )
            if hotel_amenity:
                db_hotel.hotel_amenities.append(hotel_amenity)
        await session.commit()
