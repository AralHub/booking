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
            select(
                HotelAmenityCategory.id.label("category_id"),
                HotelAmenityCategory.name.label("category_name"),
                HotelAmenity.id.label("amenity_id"),
                HotelAmenity.name.label("amenity_name"),
                HotelAmenity.icon.label("amenity_icon"),
            )
            .join(
                HotelAmenity,
                HotelAmenityCategory.id == HotelAmenity.hotel_amenity_category_id,
            )
            .join(
                HotelAmenityAssociation,
                HotelAmenity.id == HotelAmenityAssociation.hotel_amenity_id,
            )
            .where(HotelAmenityAssociation.hotel_id == hotel_id)
        )

        result = await session.execute(query)
        rows = result.all()
        categories_dict = {}

        for row in rows:
            category_id = row.category_id

            if category_id not in categories_dict:
                categories_dict[category_id] = {
                    "id": category_id,
                    "name": row.category_name,
                    "hotel_amenities": [],
                }

            categories_dict[category_id]["hotel_amenities"].append(
                {
                    "id": row.amenity_id,
                    "name": row.amenity_name,
                    "icon": row.amenity_icon,
                    "hotel_amenity_category_id": category_id,
                }
            )

        hotel_data = {
            "id": hotel_id,
            "hotel_amenity_categories": list(categories_dict.values()),
        }

        return hotel_data

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
