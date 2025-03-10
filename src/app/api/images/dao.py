from sqlalchemy.ext.asyncio import AsyncSession

from app.api.images.models import HotelImage, RoomImage
from app.core.dao import BaseDAO


class HotelImageDAO(BaseDAO):
    model = HotelImage


class RoomImageDAO(BaseDAO):
    model = RoomImage

    @classmethod
    async def add_room_image(
        cls,
        session: AsyncSession,
        room_id: int,
        image: str,
    ):
        room_image = RoomImage(
            room_id=room_id,
            image=image,
        )
        session.add(room_image)
        await session.commit()
