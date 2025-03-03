from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dao import BaseDAO

from .models import BedType, Room, RoomBedConfiguration, RoomType, RoomTypeVariant


class RoomDAO(BaseDAO):
    model = Room

    @classmethod
    async def get_hotel_room_types(cls, hotel_id: int, session: AsyncSession):
        query = (
            select(RoomType)
            .join(RoomTypeVariant)
            .join(Room)
            .where(Room.hotel_id == hotel_id)
        )
        result = await session.execute(query)
        return result.scalars().all()


class RoomTypeDAO(BaseDAO):
    model = RoomType

    @classmethod
    async def get_room_type_variants(
        cls,
        room_type_id: int,
        session: AsyncSession,
    ):
        query = (
            select(cls.model)
            .options(selectinload(cls.model.room_type_variants))
            .where(cls.model.id == room_type_id)
        )
        result = await session.execute(query)
        return result.scalars().all()


class RoomTypeVariantDAO(BaseDAO):
    model = RoomTypeVariant


class BedTypeDAO(BaseDAO):
    model = BedType


class RoomBedConfDAO(BaseDAO):
    model = RoomBedConfiguration
