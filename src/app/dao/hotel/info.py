from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BaseDAO
from app.core.exceptions.http_exceptions import NotFoundException
from app.models.hotel.info import HotelInfo
from app.models.hotel import Hotel

# from app.schemas.hotel.info import HotelInfoFilter


class HotelInfoDAO(BaseDAO):
    model = HotelInfo

    @classmethod
    async def get_hotel_info(
        cls,
        session: AsyncSession,
        hotel_id: int,
    ):
        query = (
            select(
                cls.model.id,
                cls.model.first_phone_number,
                cls.model.second_phone_number,
                cls.model.email,
                cls.model.site_url,
            )
            .join(Hotel)
            .where(Hotel.id == hotel_id)
        )

        result = await session.execute(query)
        data = result.scalar_one_or_none()
