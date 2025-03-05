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
        check_in_date: date,
        check_out_date: date,
        guest_quantity: int,
    ):
        # Определение количества свободных номеров для каждого типа
        overlapping_bookings = (
            select(Booking.room_id, func.count(Booking.id).label("booking_count"))
            .where(
                and_(
                    Booking.check_out_date > check_in_date,
                    Booking.check_in_date < check_out_date,
                    Booking.status != BookingStatus.CANCELLED,
                )
            )
            .group_by(Booking.room_id)
            .cte("overlapping_bookings")
        )
        room_availability = (
            select(
                Room.id,
                Room.hotel_id,
                Room.max_guests,
                Room.quantity,
                func.greatest(
                    0,
                    Room.quantity
                    - func.coalesce(overlapping_bookings.c.booking_count, 0),
                ).label("free_rooms"),
            )
            .outerjoin(overlapping_bookings, Room.id == overlapping_bookings.c.room_id)
            .cte("room_availability")
        )
        # Вычисление общей вместимости отеля
        hotel_capacity = (
            select(
                room_availability.c.hotel_id,
                func.sum(
                    room_availability.c.free_rooms * room_availability.c.max_guests
                ).label("total_capacity"),
            )
            .group_by(room_availability.c.hotel_id)
            .cte("hotel_capacity")
        )

        # Выборка отелей с достаточной вместимостью
        stmt = (
            select(Hotel)
            .join(hotel_capacity, Hotel.id == hotel_capacity.c.hotel_id)
            .where(hotel_capacity.c.total_capacity >= guest_quantity)
        )

        available_hotels = (await session.execute(stmt)).scalars().all()

        return available_hotels


class HotelCategoryDAO(BaseDAO):
    model = HotelCategory
