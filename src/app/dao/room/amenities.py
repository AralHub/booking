from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import IntegrityError
from app.dao import BaseDAO
from app.core.exceptions.http_exceptions import BadRequestException
from app.models.room.amenities import (
    RoomAmenity,
    RoomAmenityCategory,
    RoomAmenityAssociation,
)
from app.models.room import Room
from app.models.room.amenities import RoomAmenityAssociation


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
    async def get_room_amenities(
        cls,
        session: AsyncSession,
        room_id: int,
    ):
        query = (
            select(
                RoomAmenityCategory.id.label("category_id"),
                RoomAmenityCategory.name.label("category_name"),
                RoomAmenity.id.label("amenity_id"),
                RoomAmenity.name.label("amenity_name"),
                RoomAmenity.icon.label("amenity_icon"),
            )
            .join(
                RoomAmenity,
                RoomAmenityCategory.id == RoomAmenity.room_amenity_category_id,
            )
            .join(
                RoomAmenityAssociation,
                RoomAmenity.id == RoomAmenityAssociation.room_amenity_id,
            )
            .where(RoomAmenityAssociation.room_id == room_id)
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
                    "room_amenities": [],
                }

            categories_dict[category_id]["room_amenities"].append(
                {
                    "id": row.amenity_id,
                    "name": row.amenity_name,
                    "icon": row.amenity_icon,
                    "room_amenity_category_id": category_id,
                }
            )

        room_data = {
            "id": room_id,
            "room_amenity_categories": list(categories_dict.values()),
        }

        return room_data

    @classmethod
    async def add_amenities_to_room(
        cls,
        session: AsyncSession,
        room_id: int,
        amenities: list[int],
    ):
        query = (
            select(Room)
            .options(selectinload(Room.room_amenities))
            .where(Room.id == room_id)
        )
        result = await session.execute(query)
        db_room = result.scalar_one_or_none()
        for room_amenity_id in amenities:
            room_amenity = await cls.get_one_or_none_by_id(
                session=session,
                data_id=room_amenity_id,
            )
            if room_amenity:
                db_room.room_amenities.append(room_amenity)
        await session.commit()

    @classmethod
    async def delete_room_all_amenities(
        cls,
        room_id: int,
        session: AsyncSession,
    ):
        db_room = await session.scalar(
            select(cls.model)
            .where(cls.model.id == room_id)
            .options(selectinload(cls.model.room_amenities))
        )

        await session.execute(
            delete(RoomAmenityAssociation).where(
                RoomAmenityAssociation.room_id == room_id
            )
        )
        await session.commit()

    @classmethod
    async def delete_amenity_from_room(
        cls,
        session: AsyncSession,
        room_id: int,
        amenity_id: int,
    ):
        query = select(RoomAmenityAssociation).where(
            RoomAmenityAssociation.room_id == room_id,
            RoomAmenityAssociation.room_amenity_id == amenity_id,
        )
        result = await session.execute(query)
        amenity_association = result.scalar()
        await session.delete(amenity_association)
        await session.commit()
