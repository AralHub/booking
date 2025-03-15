from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BaseDAO
from app.schemas.room.price import RoomPriceFilter
from app.models.room.price import RoomPrice


class RoomPriceDAO(BaseDAO):
    model = RoomPrice

    @classmethod
    async def get_room_price(
        cls,
        session: AsyncSession,
        room_id: int,
    ):
        room = await cls.get_one_or_none(
            session=session,
            filters=RoomPriceFilter(
                room_id=room_id,
            ),
        )
        return room.base_price if room else None
