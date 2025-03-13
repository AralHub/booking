from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BaseDAO
from app.core.exceptions.http_exceptions import NotFoundException
from app.models.hotel.info import HotelInfo
from app.models.hotel import Hotel
from app.schemas.hotel.info import HotelInfoNameRead

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
                cls.model.id.label("id"),
                cls.model.first_phone_number.label("first_phone_number"),
                cls.model.second_phone_number.label("second_phone_number"),
                cls.model.email.label("email"),
                cls.model.site_url.label("site_url"),
                Hotel.name.label("hotel_name"),
                Hotel.description.label("hotel_description"),
                Hotel.slug.label("hotel_slug"),
                Hotel.id.label("hotel_id"),
                Hotel.hotel_category_id.label("hotel_category_id"),
            )
            .join(Hotel)
            .where(cls.model.hotel_id == hotel_id)
        )

        result = await session.execute(query)
        hotel_info = result.mappings().one_or_none()

        return HotelInfoNameRead(**hotel_info) or None
