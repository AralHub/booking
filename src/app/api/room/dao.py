# from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# from sqlalchemy.orm import selectinload
from app.core.dao import BaseDAO

from .models import BedType, Room, RoomBedConfiguration, RoomType


class RoomDAO(BaseDAO):
    model = Room

    @classmethod
    async def get_room_price(cls, session: AsyncSession, room_id: int):
        room = await cls.get_one_or_none_by_id(
            session=session,
            data_id=room_id,
        )
        return room.base_price if room else None


class RoomTypeDAO(BaseDAO):
    model = RoomType


class BedTypeDAO(BaseDAO):
    model = BedType


class RoomBedConfDAO(BaseDAO):
    model = RoomBedConfiguration
