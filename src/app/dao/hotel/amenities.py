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
    async def get_hotel_amenities(
        cls,
        session: AsyncSession,
        hotel_id: int,
    ):
        query = (
            select(Hotel)
            .where(Hotel.id == hotel_id)
            .options(selectinload(Hotel.hotel_amenities))
        )
        result = await session.execute(query)
        hotel = result.scalar()
        return hotel.hotel_amenities if hotel else []

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
        # Get existing amenity IDs
        existing_amenity_ids = {amenity.id for amenity in db_hotel.hotel_amenities}

        # Filter out amenities that already exist
        new_amenity_ids = [aid for aid in amenities if aid not in existing_amenity_ids]

        if not new_amenity_ids:
            return db_hotel.hotel_amenities
        try:
            amenity_objects = await session.execute(
                select(HotelAmenity).where(HotelAmenity.id.in_(new_amenity_ids))
            )
            amenity_objects = amenity_objects.scalars().all()
            db_hotel.hotel_amenities.extend(amenity_objects)
            await session.commit()
            return db_hotel.hotel_amenities
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
        await session.execute(
            delete(HotelAmenityAssociation).where(
                HotelAmenityAssociation.hotel_id == hotel_id
            )
        )
        await session.commit()

    @classmethod
    async def remove_amenity_from_hotel(
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
