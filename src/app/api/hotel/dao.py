from datetime import date

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.api.amenity.hotel_amenity.dao import HotelAmenityDAO
from app.api.booking.models import Booking
from app.api.locations.models import Location
from app.api.room.models import Room
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

    @classmethod
    async def find_hotels(
        cls,
        session: AsyncSession,
        city_id: int,
        check_in: str,
        check_out: str,
        guest_quantity: int,
    ):
        def parse_date(date_str: str) -> date:
            # Replace dot with hyphen for parsing
            if "." in date_str:
                date_str = date_str.replace(".", "-")
            return date.fromisoformat(date_str)

        parsed_check_in = parse_date(check_in)
        parsed_check_out = parse_date(check_out)

        subquery = (
            select(
                Room.hotel_id,
                func.count(Room.id).label("available_rooms"),
                func.sum(Room.max_guests).label("total_capacity"),
            )
            .outerjoin(
                Booking,
                and_(
                    Booking.room_id == Room.id,
                    Booking.check_in_date < parsed_check_out,
                    Booking.check_out_date > parsed_check_in,
                ),
            )
            .where(Booking.id.is_(None))
            .group_by(Room.hotel_id)
            .subquery()
        )

        stmt = (
            select(Hotel)
            .join(subquery, Hotel.id == subquery.c.hotel_id)
            .join(Location, Hotel.id == Room.hotel_id)
            .options(joinedload(Hotel.rooms))
            .where(subquery.c.total_capacity >= guest_quantity)
            .where(Location.city_id == city_id)
        )
        result = await session.execute(stmt)
        hotels = result.scalars().all()

        results = []
        for hotel in hotels:
            room_summary = {}
            for room in hotel.rooms:
                room_type = room.room_type_variant.name
                if room_type not in room_summary:
                    room_summary[room_type] = {"count": 0, "beds": []}
                room_summary[room_type]["count"] += 1
                room_summary[room_type]["beds"].append(
                    f"{room.max_guests} спальных мест"
                )

            results.append(
                {
                    "hotel_name": hotel.name,
                    "location": hotel.location.name,
                    "room_details": room_summary,
                }
            )

        return results


class HotelCategoryDAO(BaseDAO):
    model = HotelCategory
