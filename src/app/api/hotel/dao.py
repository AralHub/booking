from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.amenity.hotel_amenity.dao import HotelAmenityDAO
from app.api.room.schemas import RoomFilter
from app.core.dao import BaseDAO
from app.core.exceptions.http_exceptions import NotFoundException

from .models import Hotel, HotelCategory


class HotelDAO(BaseDAO):
    model = Hotel

    @classmethod
    async def add_hotel_amenities(
        cls,
        hotel_id: int,
        hotel_amenities_data: list[int],
        session: AsyncSession,
    ):
        query = (
            select(cls.model)
            .options(selectinload(cls.model.hotel_amenities))
            .where(cls.model.id == hotel_id)
        )
        result = await session.execute(query)
        db_hotel = result.scalar_one_or_none()
        if not db_hotel:
            raise NotFoundException("Hotel not found")
        for hotel_amenity_id in hotel_amenities_data:
            hotel_amenity = await HotelAmenityDAO.get_one_or_none_by_id(
                session=session,
                data_id=hotel_amenity_id,
            )
            if hotel_amenity:
                db_hotel.hotel_amenities.append(hotel_amenity)
        await session.commit()

    @classmethod
    async def get_hotel_amenities(cls, hotel_id: int, session: AsyncSession):
        query = (
            select(cls.model)
            .options(selectinload(cls.model.hotel_amenities))
            .where(cls.model.id == hotel_id)
        )
        result = await session.execute(query)
        db_hotel = result.scalar_one_or_none()

        if not db_hotel:
            raise NotFoundException("Hotel not found")
        return db_hotel.hotel_amenities

    # @classmethod
    # async def find_hotels(
    #     cls,
    #     session: AsyncSession,
    #     city_id: int,
    #     check_in_date: date,
    #     check_out_date: date,
    #     guest_quantity: int,
    # ):
    #     # Подзапрос для подсчета суммарной вместимости свободных комнат в отеле
    #     available_capacity_subquery = (
    #         select(func.sum(Room.max_guests).label("total_guests"))
    #         .select_from(Room)
    #         .where(
    #             Room.hotel_id == Hotel.id,  # Связь с текущим отелем
    #             Room.quantity > 0,  # Комната доступна в количестве
    #             ~exists().where(  # Нет пересекающихся броней
    #                 and_(
    #                     Booking.room_id == Room.id,
    #                     Booking.check_in_date < check_out_date,
    #                     Booking.check_out_date > check_in_date,
    #                 )
    #             ),
    #         )
    #     ).scalar_subquery()

    #     # Основной запрос: отели в указанном городе с суммарной вместимостью >= guest_quantity
    #     hotels_query = select(Hotel).where(
    #         Hotel.location.has(city_id=city_id),
    #         available_capacity_subquery >= guest_quantity,  # Проверка общей вместимости
    #     )

    #     result = await session.execute(hotels_query)
    #     return result.scalars().all()
    @classmethod
    async def find_hotels(
        cls,
        session: AsyncSession,
        city_id: int,
        check_in_date: date,
        check_out_date: date,
        rooms: list[RoomFilter],
    ):
        pass


class HotelCategoryDAO(BaseDAO):
    model = HotelCategory
