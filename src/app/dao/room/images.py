from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BaseDAO
from app.models.room.images import RoomImage
from app.schemas.room.images import RoomImageFilter
from app.core.config import settings


class RoomImageDAO(BaseDAO):
    model = RoomImage

    @classmethod
    async def add_room_image(
        cls,
        session: AsyncSession,
        room_id: int,
        file_path: str,
    ):
        images_count = cls.count(
            session=session,
            filters=RoomImageFilter(
                room_id=room_id,
            ),
        )
        return await cls.create(
            session=session,
            values=RoomImageFilter(
                room_id=room_id,
                position=images_count + 1,
                image=f"{settings.image_base_url}{file_path}",
            ),
        )
