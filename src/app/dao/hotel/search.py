import asyncio
from datetime import date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.exceptions.http_exceptions import NotFoundException

from app.dao.location import CityDAO
from app.dao.booking import BookingDAO
from app.dao.hotel import HotelDAO
from app.models.room.price import RoomPrice
from app.models.hotel.amenities import HotelAmenityAssociation
from app.models.hotel import Hotel
from app.models.hotel.location import HotelLocation
from app.models.room import Room

from app.schemas.location import CityFilter
from app.schemas.room import RoomRead
from app.schemas.hotel.images import HotelImageRead


class HotelSearchDAO(HotelDAO):

    @classmethod
    async def find_hotels_for_booking(
        cls,
        session: AsyncSession,
        city: str,
        check_in_date: date,
        check_out_date: date,
        guests: list[int],
        price_min: float = None,
        price_max: float = None,
        max_distance_to_center: float = None,
        amenities: list[int] = None,
    ):
        # Находим город и отели в нем
        hotel_ids = await cls._find_hotels_in_city(
            session,
            city,
            max_distance_to_center,
            amenities,
        )

        if not hotel_ids:
            return None

        # Получаем доступные комнаты
        available_rooms = await cls._get_available_rooms(
            session,
            hotel_ids,
            check_in_date,
            check_out_date,
            price_min,
            price_max,
            guests,
        )

        if not available_rooms:
            return None

        # Группируем доступные комнаты по отелям (ключ – hotel_id, значение – список комнат)
        available_rooms_by_hotel = {}
        for room in available_rooms:
            available_rooms_by_hotel.setdefault(room.hotel_id, []).append(room)

        if not available_rooms_by_hotel:
            return None

        # Идентификаторы отелей с доступными комнатами
        suitable_hotel_ids = list(available_rooms_by_hotel.keys())

        # Загружаем полную информацию о подходящих отелях
        return await cls._load_hotels_full_info(
            session,
            suitable_hotel_ids,
            available_rooms_by_hotel,
        )

    @classmethod
    async def _find_hotels_in_city(
        cls,
        session: AsyncSession,
        city: str,
        max_distance_to_center: float = None,
        amenities: list[int] = None,
    ):
        # Находим город
        db_city = await CityDAO.get_one_or_none(
            session=session,
            filters=CityFilter(slug=city),
        )
        if not db_city:
            raise NotFoundException("City not found")

        # Базовый запрос для отелей в городе
        hotels_query = (
            select(Hotel.id)
            .join(HotelLocation, Hotel.id == HotelLocation.hotel_id)
            .where(HotelLocation.city_id == db_city.id)
        )

        # Фильтр по расстоянию до центра, если указан
        if max_distance_to_center is not None:
            hotels_query = hotels_query.where(
                HotelLocation.to_city_center <= max_distance_to_center
            )

        # Фильтр по удобствам, если указаны
        if amenities and len(amenities) > 0:
            amenities_subquery = (
                select(HotelAmenityAssociation.hotel_id)
                .where(HotelAmenityAssociation.hotel_amenity_id.in_(amenities))
                .group_by(HotelAmenityAssociation.hotel_id)
                .having(
                    func.count(HotelAmenityAssociation.hotel_amenity_id)
                    == len(amenities)
                )
                .scalar_subquery()
            )
            hotels_query = hotels_query.where(Hotel.id.in_(amenities_subquery))

        # Получаем отели с учетом фильтров
        hotels_result = await session.execute(hotels_query)
        return hotels_result.scalars().all()

    @classmethod
    async def _get_available_rooms(
        cls,
        session: AsyncSession,
        hotel_ids: list[int],
        check_in_date: date,
        check_out_date: date,
        price_min: float = None,
        price_max: float = None,
        guests: list[int] = None,
    ):
        # Получаем все комнаты для указанных отелей
        rooms_query = (
            select(Room)
            .options(
                selectinload(Room.room_type),
                selectinload(Room.room_prices),
            )
            .where(Room.hotel_id.in_(hotel_ids))
        )

        # Фильтр по цене, если указан
        if price_min is not None:
            rooms_query = rooms_query.where(Room.base_price >= price_min)
        if price_max is not None:
            rooms_query = rooms_query.where(Room.base_price <= price_max)

        rooms_result = await session.execute(rooms_query)
        all_rooms = rooms_result.scalars().all()

        available_rooms = []

        # Для каждого отеля получаем количество забронированных комнат и фильтруем комнаты
        for hotel_id in hotel_ids:
            booked_rooms_count = await BookingDAO.get_booked_rooms_count_by_hotel_id(
                session=session,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                hotel_id=hotel_id,
            )

            # Отбираем комнаты, принадлежащие конкретному отелю
            hotel_rooms = [room for room in all_rooms if room.hotel_id == hotel_id]

            for room in hotel_rooms:
                room_id = room.id
                room_quantity = getattr(room, "quantity", 1)
                booked_count = booked_rooms_count.get(room_id, 0)

                # Если комната полностью забронирована, пропускаем её
                if booked_count >= room_quantity:
                    continue

                # Проверяем доступность для каждого значения количества гостей
                if guests is None:
                    is_available = await BookingDAO.is_room_available(
                        session=session,
                        room=room,
                        check_in_date=check_in_date,
                        check_out_date=check_out_date,
                        guest_quantity=1,
                    )
                else:
                    # Параллельно проверяем доступность для каждого значения количества гостей
                    check_results = await asyncio.gather(
                        *[
                            BookingDAO.is_room_available(
                                session=session,
                                room=room,
                                check_in_date=check_in_date,
                                check_out_date=check_out_date,
                                guest_quantity=guest_count,
                            )
                            for guest_count in guests
                        ]
                    )
                    is_available = all(check_results)

                if is_available:
                    available_rooms.append(room)

        return available_rooms

    @classmethod
    async def _load_hotels_full_info(
        cls,
        session: AsyncSession,
        hotel_ids: list[int],
        selected_rooms: dict,
    ):
        # Загружаем полную информацию о подходящих отелях одним запросом
        hotels_query = (
            select(Hotel)
            .options(
                selectinload(Hotel.hotel_rating),
                selectinload(Hotel.location).selectinload(HotelLocation.city),
                selectinload(Hotel.hotel_category),
                selectinload(Hotel.hotel_images),
                selectinload(Hotel.reviews),
            )
            .where(Hotel.id.in_(hotel_ids))
        )

        hotels_result = await session.execute(hotels_query)
        hotels = hotels_result.scalars().all()

        # Формируем окончательный результат
        suitable_hotels_data = []
        for hotel in hotels:
            rooms = selected_rooms.get(hotel.id, [])

            min_price, min_price_guests = HotelDAO._get_min_price_and_guests(rooms)
            hotel_data = {
                "id": hotel.id,
                "name": hotel.name,
                "description": hotel.description,
                "slug": hotel.slug,
                "rating": (
                    hotel.hotel_rating.average_rating if hotel.hotel_rating else None
                ),
                "reviews_count": len(hotel.reviews) if hotel.reviews else 0,
                "category": hotel.hotel_category.name if hotel.hotel_category else None,
                "images": [
                    HotelImageRead.model_validate(image)
                    for image in hotel.hotel_images
                ]
                if hotel.hotel_images
                else [],
                "location": (
                    {
                        "address": hotel.location.address,
                        "city": (
                            hotel.location.city.name if hotel.location.city else None
                        ),
                        "coordinates": {
                            "latitude": hotel.location.latitude,
                            "longitude": hotel.location.longitude,
                        },
                        "distance_to_center": hotel.location.to_city_center,
                    }
                    if hotel.location
                    else None
                ),
                "min_price": min_price,
                "guests": min_price_guests,
            }
            suitable_hotels_data.append(hotel_data)

        return suitable_hotels_data
