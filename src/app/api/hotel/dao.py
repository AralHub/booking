from datetime import date

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from app.core.dao import BaseDAO
from app.core.exceptions.http_exceptions import NotFoundException

from app.api.room.dao import RoomDAO
from app.api.room.models import Room
from app.api.room.schemas import RoomFilter
from app.api.locations.dao import LocationDAO
from app.api.locations.models import Location
from app.api.amenity.hotel_amenity.dao import HotelAmenityDAO
from app.api.booking.models import Booking, BookingStatus
from .models import Hotel, HotelCategory
from .schemas import HotelFilter


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

    @classmethod
    async def find_hotels(
        cls,
        session: AsyncSession,
        city_id: int,
        check_in: date,
        check_out: date,
        guest_quantity: int,
    ):

        hotels_query = select(Hotel).join(Location).where(Location.city_id == city_id)
        hotels = (await session.execute(hotels_query)).scalars().all()
        for hotel in hotels:
            rooms = await RoomDAO.get_all(
                session=session,
                filters=RoomFilter(
                    hotel_id=hotel.id,
                ),
            )
        for room in rooms:
            bookings = await session.execute(
                select(Booking).filter(
                    Booking.room_id == room.id,
                    Booking.check_in_date <= check_in,
                    Booking.check_out_date >= check_out,
                )
            )
            bookings = bookings.scalars().all()
        return bookings
        # Подзапрос для подсчета активных бронирований по комнатам


        # # Основной запрос
        # stmt = (
        #     select(Hotel)
        #     .join(Hotel.rooms)
        #     .outerjoin(booked_cte, Room.id == booked_cte.c.room_id)
        #     .where(
        #         and_(
        #             Room.max_guests >= guest_quantity,
        #             Room.quantity > func.coalesce(booked_cte.c.booked_count, 0),
        #         )
        #     )
        #     .options(selectinload(Hotel.rooms))  # Жадно загружаем комнаты
        #     .distinct()
        # )

        # result = await session.execute(stmt)
        # return result.scalars().all()


class HotelCategoryDAO(BaseDAO):
    model = HotelCategory
