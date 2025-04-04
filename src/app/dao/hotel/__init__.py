from datetime import UTC, date, datetime

from fastapi import Depends
from sqlalchemy import delete, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.exceptions.http_exceptions import NotFoundException
from app.core.utils.slug_utils import generate_slug_for_hotel
from app.api.dependencies.hotel import validate_hotel

from app.dao import BaseDAO
from app.dao.hotel.amenities import HotelAmenityDAO
from app.dao.hotel.location import HotelLocationDAO
from app.dao.location import CityDAO
from app.dao.review import ReviewDAO
from app.dao.hotel.category import HotelCategoryDAO
from app.dao.hotel.info import HotelInfoDAO
from app.dao.room import RoomDAO
from app.dao.booking import BookingDAO
from app.dao.hotel.rules import HotelRuleDAO

from app.models.hotel.amenities import HotelAmenityAssociation
from app.models.booking import Booking
from app.schemas.hotel.location import (
    LocationCreate,
    LocationFilter,
    LocationUpdate,
)
from app.models.hotel import Hotel
from app.models.room.price import RoomPrice
from app.models.hotel.category import HotelCategory
from app.models.hotel.location import HotelLocation
from app.models.booking import BookingStatus
from app.models.room import Room
from app.models.hotel.location import HotelLocation
from app.models.hotel.rating import HotelRating

from app.schemas.location import CityFilter
from app.schemas.hotel.category import HotelCategoryFilter
from app.schemas.hotel.info import HotelInfoFilter, HotelInfoUpdate
from app.schemas.hotel.info import (
    HotelInfoCreateInternal,
    HotelInfoFilter,
    HotelInfoUpdate,
    HotelNameRead,
    HotelNameCreateInternal,
    HotelNameFilter,
    HotelNameUpdate,
)
from app.schemas.hotel.rules import (
    RuleCreateInternal,
    RuleFilter,
    RuleUpdate,
)
from app.schemas.hotel import HotelFullCreate, HotelFullUpdate


class HotelDAO(BaseDAO):
    model = Hotel

    @classmethod
    async def get_popular_hotels(
        cls,
        session: AsyncSession,
        limit: int,
    ):
        min_price_subquery = (
            select(
                Room.hotel_id,
                func.min(Room.base_price).label("min_price"),
                func.first_value(Room.id)
                .over(partition_by=Room.hotel_id, order_by=Room.base_price)
                .label("cheapest_room_id"),
            )
            .group_by(Room.hotel_id, Room.id)
            .subquery()
        )

        query = (
            select(cls.model)
            .join(HotelRating, cls.model.id == HotelRating.hotel_id)
            .join(min_price_subquery, cls.model.id == min_price_subquery.c.hotel_id)
            .join(Room, Room.id == min_price_subquery.c.cheapest_room_id)
            .options(
                selectinload(cls.model.hotel_rating),
                selectinload(cls.model.location),
                selectinload(
                    cls.model.rooms.and_(
                        Room.id == min_price_subquery.c.cheapest_room_id
                    )
                ).selectinload(Room.room_prices),
            )
            .order_by(HotelRating.average_rating.desc())
            .limit(limit)
        )

        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_full_hotel_by_id(cls, hotel_id: int, session: AsyncSession):
        query = (
            select(cls.model)
            .options(
                selectinload(cls.model.hotel_amenities),
                selectinload(cls.model.hotel_info),
                selectinload(cls.model.location).selectinload(HotelLocation.city),
                selectinload(cls.model.rule),
                selectinload(cls.model.reviews),
                selectinload(cls.model.hotel_category),
            )
            .where(cls.model.id == hotel_id)
        )
        result = await session.execute(query)
        hotel = result.scalar_one_or_none()
        return hotel or None

    @classmethod
    async def create_new_hotel(
        cls,
        hotel_create_data: HotelFullCreate,
        session: AsyncSession,
        hotel_admin_id: int,
    ):
        db_hotel_category = await HotelCategoryDAO.get_one_or_none(
            session=session,
            filters=HotelCategoryFilter(id=hotel_create_data.hotel_category_id),
        )

        if not db_hotel_category:
            raise NotFoundException("Hotel category not found")
        db_city = await CityDAO.get_one_or_none(
            session=session,
            filters=CityFilter(
                id=hotel_create_data.city_id,
            ),
        )
        if not db_city:
            raise NotFoundException("City not found")
        generated_slug = await generate_slug_for_hotel(
            session=session,
            name=hotel_create_data.name_en,
        )
        hotel_create_internal = HotelNameCreateInternal(
            name=hotel_create_data.to_dict_name(),
            description=hotel_create_data.to_dict_description(),
            slug=generated_slug,
            hotel_category_id=hotel_create_data.hotel_category_id,
            hotel_admin_id=hotel_admin_id,
            is_active=False,
            created_at=datetime.now(UTC),
        )
        # Create main hotel record
        db_hotel = await HotelDAO.create(
            session=session,
            values=hotel_create_internal,
        )
        # Create hotel info
        await HotelInfoDAO.create(
            session=session,
            values=HotelInfoCreateInternal(
                hotel_id=db_hotel.id,
                first_phone_number=hotel_create_data.information_for_guests.first_phone_for_guests,
                second_phone_number=hotel_create_data.information_for_guests.second_phone_for_guests,
                email=hotel_create_data.information_for_guests.email_for_guests,
                site_url=hotel_create_data.information_for_guests.site_url,
            ),
        )
        # Create location record
        await HotelLocationDAO.add_hotel_location(
            session=session,
            location_create_data=LocationCreate(
                address=hotel_create_data.address,
                city_id=hotel_create_data.city_id,
                longitude=hotel_create_data.longitude,
                latitude=hotel_create_data.latitude,
            ),
            hotel_id=db_hotel.id,
        )
        # Create hotel rules
        await HotelRuleDAO.create(
            session=session,
            values=RuleCreateInternal(
                hotel_id=db_hotel.id,
                check_in_from=(
                    hotel_create_data.information_for_booking.check_in
                    if hotel_create_data.information_for_booking.check_in
                    else None
                ),
                check_out_from=(
                    hotel_create_data.information_for_booking.check_out
                    if hotel_create_data.information_for_booking.check_out
                    else None
                ),
            ),
        )
        # Add hotel amenities
        if hotel_create_data.facilities:
            await HotelAmenityDAO.add_hotel_amenities(
                session=session,
                hotel_id=db_hotel.id,
                amenities=hotel_create_data.facilities,
            )
        return db_hotel

    @classmethod
    async def update_hotel(
        cls,
        hotel_update_data: HotelFullUpdate,
        session: AsyncSession,
        hotel_id: int,
        hotel: HotelNameRead = Depends(validate_hotel),
    ):
        # Validate hotel category exists
        db_hotel_category = await HotelCategoryDAO.get_one_or_none(
            session=session,
            filters=HotelCategoryFilter(id=hotel_update_data.hotel_category_id),
        )
        if not db_hotel_category:
            raise NotFoundException("Hotel category not found")
        generated_slug = await generate_slug_for_hotel(
            name=hotel_update_data.name,
        )
        hotel_update = HotelNameUpdate(
            name=hotel_update_data.name,
            description=hotel_update_data.description,
            slug=generated_slug,
            hotel_category_id=hotel_update_data.hotel_category_id,
        )
        # Create main hotel record
        await cls.update(
            session=session,
            values=hotel_update,
            filters=HotelNameFilter(
                id=hotel_id,
            ),
        )
        # Create hotel info
        await HotelInfoDAO.update(
            session=session,
            values=HotelInfoUpdate(
                first_phone_number=hotel_update_data.information_for_guests.first_phone_for_guests,
                second_phone_number=hotel_update_data.information_for_guests.second_phone_for_guests,
                email=hotel_update_data.information_for_guests.email_for_guests,
                site_url=hotel_update_data.information_for_guests.site_url,
            ),
            filters=HotelInfoFilter(
                hotel_id=hotel_id,
            ),
        )
        # Create location record
        await HotelLocationDAO.update_hotel_location(
            session=session,
            location_update_data=LocationUpdate(
                address=hotel_update_data.address,
                latitude=hotel_update_data.latitude,
                longitude=hotel_update_data.longitude,
                city_id=hotel_update_data.city_id,
            ),
            hotel_id=hotel_id,
        )
        # Create hotel rules
        await HotelRuleDAO.update(
            session=session,
            values=RuleUpdate(
                check_in_from=(
                    hotel_update_data.information_for_booking.check_in
                    if hotel_update_data.information_for_booking.check_in
                    else None
                ),
                check_out_from=(
                    hotel_update_data.information_for_booking.check_out
                    if hotel_update_data.information_for_booking.check_out
                    else None
                ),
            ),
            filters=RuleFilter(hotel_id=hotel_id),
        )
        # Add hotel amenities
        if hotel_update_data.facilities:
            await HotelAmenityDAO.add_hotel_amenities(
                session=session,
                hotel_id=hotel_id,
                hotel_amenities_data=hotel_update_data.facilities,
            )

        return hotel

    @classmethod
    async def find_hotels_for_booking(
        cls,
        session: AsyncSession,
        city: str,
        check_in_date: date,
        check_out_date: date,
        guests: list[
            int
        ],  # Список размеров групп гостей (например, [2, 1] = 2 комнаты)
        price_min: float = None,
        price_max: float = None,
        max_distance_to_center: float = None,
        amenities: list[int] = None,
    ):
        db_city = await CityDAO.get_one_or_none(
            session=session,
            filters=CityFilter(slug=city),
        )
        if not db_city:
            raise NotFoundException("City not found")

        hotels_in_city = await session.execute(
            select(Hotel.id)
            .join(HotelLocation, Hotel.id == HotelLocation.hotel_id)
            .where(HotelLocation.city_id == db_city.id)
        )
        hotel_ids = hotels_in_city.scalars().all()
        # Получить перекрывающиеся бронирования
        overlapping_bookings = await BookingDAO.get_bookings_by_hotel_ids(
            session=session,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            hotel_ids=hotel_ids,
        )

        # Извлекаем идентификаторы забронированных комнат
        booked_room_ids = []
        for booking in overlapping_bookings:
            for room_info in booking.rooms_info:
                booked_room_ids.append(room_info["room_id"])

        print(f"Забронированные номера: {booked_room_ids}")
        print(f"Требуемое размещение гостей: {guests}")
        # chessboard_subquery = (
        #     select(ChessBoard.room_type_id)
        #     .where(
        #         ChessBoard.check_date.between(check_in_date, check_out_date),
        #         (ChessBoard.is_closed == True)  # комната закрыта
        #         | (ChessBoard.available_rooms_count <= 0),  # нет доступных комнат
        #     )
        #     .subquery()
        # )
        # rooms_query = (
        #     select(Room)
        #     .join(Hotel, Room.hotel_id == Hotel.id)
        #     .join(HotelLocation, Hotel.id == HotelLocation.hotel_id)
        #     .where(
        #         Room.id.not_in(booked_room_ids) if booked_room_ids else True,
        #         # Исключаем комнаты, чьи типы имеют ограничения на выбранные даты
        #         Room.room_type_id.not_in(chessboard_subquery),
        #     )
        #     .options(
        #         selectinload(Room.hotel),
        #         selectinload(Room.room_type),
        #         selectinload(Room.bed_configurations),
        #     )
        # )
        # Получаем все доступные комнаты в городе
        rooms_query = (
            select(Room)
            .join(Hotel, Room.hotel_id == Hotel.id)
            .join(HotelLocation, Hotel.id == HotelLocation.hotel_id)
            .where(
                Room.id.not_in(booked_room_ids) if booked_room_ids else True,
            )
            .options(
                selectinload(Room.hotel),
                selectinload(Room.room_type),
                selectinload(Room.bed_configurations),
            )
        )

        available_rooms = await session.execute(rooms_query)
        available_rooms = available_rooms.scalars().all()

        print(f"Всего доступных номеров: {len(available_rooms)}")

        # Если нет доступных номеров, возвращаем пустой список
        if not available_rooms:
            return []

        # Группируем комнаты по отелям
        hotels_with_rooms = {}
        for room in available_rooms:
            if room.hotel_id not in hotels_with_rooms:
                hotels_with_rooms[room.hotel_id] = []
            hotels_with_rooms[room.hotel_id].append(room)

        # Список для хранения результатов
        suitable_hotels_data = []

        for hotel_id, rooms in hotels_with_rooms.items():
            # Сортируем комнаты по вместимости в порядке убывания
            sorted_rooms = [
                room
                for _, room in sorted(
                    [(room.max_guests, room) for room in rooms], reverse=True
                )
            ]

            # Копия списка гостей для манипуляций
            remaining_guests = guests.copy()
            remaining_guests.sort(reverse=True)  # Сортируем по убыванию

            used_rooms = []
            all_guests_accommodated = True

            # Проверяем размещение всех гостей
            for group_size in remaining_guests:
                room_found = False

                # Ищем идеальное совпадение
                for i, room in enumerate(sorted_rooms):
                    if i in used_rooms:
                        continue

                    if room.max_guests == group_size:
                        used_rooms.append(i)
                        room_found = True
                        break

                # Если идеального совпадения нет, ищем комнату большей вместимости
                if not room_found:
                    for i, room in enumerate(sorted_rooms):
                        if i in used_rooms:
                            continue

                        if room.max_guests >= group_size:
                            used_rooms.append(i)
                            room_found = True
                            break

                if not room_found:
                    all_guests_accommodated = False
                    break

            if all_guests_accommodated:
                # Загружаем отель с необходимыми данными
                hotel = await cls.get_full_hotel_by_id(hotel_id, session)
                if hotel:
                    # Создаем структуру данных вместо прямой модификации объекта
                    hotel_data = {
                        "id": hotel.id,
                        "name": hotel.name,
                        "description": hotel.description,
                        "slug": hotel.slug,
                        "category_name": (
                            hotel.hotel_category.name if hotel.hotel_category else None
                        ),
                        "location": (
                            {
                                "address": hotel.location.address,
                                "city": (hotel.location.city.name),
                                "coordinates": (
                                    {
                                        "latitude": hotel.location.latitude,
                                        "longitude": hotel.location.longitude,
                                    }
                                ),
                                "distance_to_center": (hotel.location.to_city_center),
                            }
                            if hotel.location
                            else None
                        ),
                        "reviews_count": len(hotel.reviews) if hotel.reviews else 0,
                        "available_rooms": [
                            {
                                "room_id": sorted_rooms[i].id,
                                "max_guests": sorted_rooms[i].max_guests,
                                "type": (
                                    sorted_rooms[i].room_type.name
                                    if sorted_rooms[i].room_type
                                    else None
                                ),
                            }
                            for i in used_rooms
                        ],
                    }
                    suitable_hotels_data.append(hotel_data)

        return suitable_hotels_data
