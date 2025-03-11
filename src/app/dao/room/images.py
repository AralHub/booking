from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BaseDAO
from app.models.room.images import RoomImage


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
