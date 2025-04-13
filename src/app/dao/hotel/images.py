from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BaseDAO
from app.models.hotel.images import HotelImage

from app.core.exceptions.http_exceptions import NotFoundException
from app.core.utils import file_utils
from app.schemas.hotel.images import HotelImageFilter
from app.core.i18n.translations import ErrorCode
from app.core.config import settings


class HotelImageDAO(BaseDAO):
    model = HotelImage

    @classmethod
    async def get_hotel_images(
        cls,
        session: AsyncSession,
        hotel_id: int,
    ):
        db_hotel_images = await cls.get_all(
            session=session,
            filters=HotelImageFilter(
                hotel_id=hotel_id,
            ),
            order_by=[HotelImage.position.asc()],
        )

        if not db_hotel_images:
            return None
        return db_hotel_images

    @classmethod
    async def add_hotel_image(
        cls,
        session: AsyncSession,
        hotel_id: int,
        file_path: str,
    ):
        images_count = cls.count(
            session=session,
            filters=HotelImageFilter(
                hotel_id=hotel_id,
            ),
        )
        return await cls.create(
            session=session,
            values=HotelImageFilter(
                hotel_id=hotel_id,
                position=images_count + 1,
                image=f"{settings.image_base_url}{file_path}",
            ),
        )

    @classmethod
    async def delete_hotel_image(
        cls,
        session: AsyncSession,
        hotel_id: int,
        image_id: int,
    ):
        image = await cls.get_one(
            session=session,
            filters=HotelImageFilter(
                hotel_id=hotel_id,
                id=image_id,
            ),
        )

        if not image:
            raise NotFoundException("Image not found")
        await file_utils.delete_photo(
            photo_path=image.image,
        )
        await cls.delete(
            session=session,
            filters=HotelImageFilter(
                hotel_id=hotel_id,
                id=image_id,
            ),
        )
