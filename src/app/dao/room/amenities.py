from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from app.dao import BaseDAO
from app.core.exceptions.http_exceptions import BadRequestException
from app.models.room.amenities import (
    RoomAmenity,
    RoomAmenityCategory,
)
from app.models.room import Room


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
        query = select(cls.model).filter_by(room_id=room_id)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def add_amenities_to_room(
        cls,
        session: AsyncSession,
        room_id: int,
        room_amenities: list[int],
    ):
        db_room = await session.scalar(
            select(Room)
            .where(Room.id == room_id)
            .options(selectinload(Room.room_amenities))
        )
        # Get existing amenity IDs
        existing_amenity_ids = {amenity.id for amenity in db_room.hotel_amenities}

        # Filter out amenities that already exist
        new_amenity_ids = [
            aid for aid in room_amenities if aid not in existing_amenity_ids
        ]

        if not new_amenity_ids:
            return db_room.hotel_amenities
        try:
            amenity_objects = await session.execute(RoomAmenity)
            amenity_objects = amenity_objects.scalars().all()
            db_room.room_amenities.extend(amenity_objects)
            await session.commit()
            return db_room.room_amenities
        except IntegrityError as e:
            await session.rollback()
            if "uq_product_extra_product" in str(e):
                raise BadRequestException(
                    detail="This amenity is already added to the hotel",
                )
            raise BadRequestException(
                detail="Unable to add amenity to hotel due to database constraint",
            )
