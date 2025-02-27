from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dao import BaseDAO

from .models import Room, RoomType, RoomTypeVariant


class RoomDAO(BaseDAO):
    model = Room


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
