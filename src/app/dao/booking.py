import uuid as uuid_pkg
from datetime import date, timedelta
from sqlalchemy import func, select, and_, or_
from sqlalchemy.orm import selectinload, joinedload, load_only
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.i18n.translations import ErrorCode
from app.core.exceptions.http_exceptions import BadRequestException, NotFoundException
from app.core.utils import redis_booking

from app.dao import BaseDAO

# from app.dao.hotel import HotelDAO
# from app.dao.hotel.images import HotelImageDAO
# from app.dao.hotel.location import HotelLocationDAO
from app.dao.room import RoomDAO
from app.dao.room.price import RoomPriceDAO
from app.dao.room.types import RoomTypeDAO

from app.models.hotel.location import HotelLocation
from app.models.location import City
from app.models.user import User
from app.models.hotel import Hotel
from app.models.booking import (
    Booking,
    BookingStatus,
    BookingType,
    BookedRoom,
)
from app.models.payment import PaymentMethod
from app.models.room import Room
from app.models.room.types import RoomType
from app.schemas.room.price import RoomPriceFilter
from app.schemas.room import RoomFilter
from app.schemas.booking import (
    BookingCreateMultipleRooms,
    BookingCreateMultipleRoomsInternal,
    BookedRoomCreateInternal,
    BookingCreateMultipleRooms,
    BookingFilter,
    RoomInfoCreateInternal,
    BookingInitialCreate,
    BookingInitialCreateInternal,
    BookingUpdateInternal,
)
from app.schemas.room.types import RoomTypeFilter

import logging

logger = logging.getLogger(__name__)


class BookedRoomDAO(BaseDAO):
    model = BookedRoom


class BookingDAO(BaseDAO):
    model = Booking

    # region Create Booking
    @classmethod
    async def create_booking(
        cls,
        session: AsyncSession,
        booking_data: BookingCreateMultipleRooms,
        user_id: int,
        hotel_id: int,
    ):
        # проверка на корректность дат
        if booking_data.check_in_date >= booking_data.check_out_date:
            raise BadRequestException(
                detail="Check-out date must be after check-in date"
            )
        total_price = 0
        total_days = (booking_data.check_out_date - booking_data.check_in_date).days

        # Проверяем доступность комнат
        await cls.check_rooms_availability(
            session=session,
            check_in_date=booking_data.check_in_date,
            check_out_date=booking_data.check_out_date,
            hotel_id=hotel_id,
            rooms_info=booking_data.rooms_info,
        )

        # Расчет общей стоимости
        room_prices = {}
        total_guests = 0
        for room in booking_data.rooms_info:
            db_room = await RoomDAO.get_one_or_none(
                session=session,
                filters=RoomFilter(
                    id=room.room_id,
                    hotel_id=hotel_id,
                ),
            )

            # Расчет цены
            room_price = await cls._calculate_room_price(
                session,
                db_room,
                room.guest_quantity,
            )

            room_total_price = total_days * room_price
            total_price += room_total_price
            room_prices[room.room_id] = room_price
            total_guests += room.guest_quantity
        # Создаем бронирование

        booking_create_data = BookingCreateMultipleRoomsInternal(
            check_in_date=booking_data.check_in_date,
            check_out_date=booking_data.check_out_date,
            total_days=total_days,
            total_price=total_price,
            total_guests=total_guests,
            special_requests=getattr(
                booking_data,
                "special_requests",
                None,
            ),
            hotel_id=hotel_id,
            status=BookingStatus.BOOKED,
            user_id=user_id,
            booking_type=booking_data.booking_type,
            payment_method_id=booking_data.payment_method_id,
            time=booking_data.time,
        )
        created_booking = await cls.create(
            session=session,
            values=booking_create_data,
        )
        logger.info(f"Created booking: {created_booking}")
        for room in booking_data.rooms_info:
            room_price = room_prices.get(room.room_id)
            await BookedRoomDAO.create(
                session=session,
                values=BookedRoomCreateInternal(
                    booking_id=created_booking.id,
                    room_id=room.room_id,
                    guest_quantity=room.guest_quantity,
                    guest_name=room.guest_name,
                    room_price=room_price,
                ),
            )

        return created_booking

    # endregion
    # region Check Rooms
    @classmethod
    async def check_rooms_availability(
        cls,
        session: AsyncSession,
        check_in_date: date,
        check_out_date: date,
        hotel_id: int,
        rooms_info: list,
    ) -> None:
        """
        Проверяет доступность комнат для бронирования на указанные даты.
        Вызывает исключение, если комнаты недоступны.
        """
        logger.info(
            f"Проверка доступности комнат для отеля {hotel_id} с {check_in_date} по {check_out_date}"
        )

        # Считаем, сколько каждой комнаты запрашивается в текущем бронировании
        requested_rooms_count = {}
        for room_info in rooms_info:
            requested_rooms_count[room_info.room_id] = (
                requested_rooms_count.get(room_info.room_id, 0) + 1
            )

        logger.info(
            f"Запрашиваемое количество комнат в этом бронировании: {requested_rooms_count}"
        )

        # Получаем все пересекающиеся бронирования для отеля
        booked_rooms_count = await cls.get_booked_rooms_count_by_hotel_id(
            session=session,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            hotel_id=hotel_id,
        )

        logger.info(f"Booked rooms count for hotel {hotel_id}: {booked_rooms_count}")

        # Проверяем каждую комнату
        checked_room_ids = set()
        for room_info in rooms_info:
            room_id = room_info.room_id

            # Пропускаем, если уже проверили эту комнату
            if room_id in checked_room_ids:
                continue

            checked_room_ids.add(room_id)
            logger.info(f"Checking room ID {room_id} for availability")

            db_room = await RoomDAO.get_one_or_none(
                session=session,
                filters=RoomFilter(
                    id=room_id,
                    hotel_id=hotel_id,
                ),
            )
            if not db_room:
                raise NotFoundException(
                    error_code=ErrorCode.NOT_FOUND,
                    detail=f"Room with ID {room_id} not found",
                )

            room_quantity = getattr(db_room, "quantity", 1)
            current_booked_count = booked_rooms_count.get(room_id, 0)
            requested_count = requested_rooms_count.get(room_id, 0)

            logger.info(
                f"Room {room_id}: Quantity={room_quantity}, Already booked={current_booked_count}, "
                f"Requested in this booking={requested_count}"
            )

            # Проверка доступности комнаты с учетом количества
            if current_booked_count + requested_count > room_quantity:
                logger.error(
                    f"Room {room_id} is not available in requested quantity: "
                    f"Requested={requested_count}, Available={room_quantity-current_booked_count}"
                )
                raise BadRequestException(
                    error_code=ErrorCode.BAD_REQUEST,
                    detail=f"Room {room_id} is not available in requested quantity",
                )

            # Проверка количества гостей
            if room_info.guest_quantity > db_room.max_guests:
                raise BadRequestException(
                    error_code=ErrorCode.BAD_REQUEST,
                    detail=f"Room {room_id} can only accommodate {db_room.max_guests} guests",
                )

        logger.info("Все комнаты доступны для бронирования")

    # endregion
    # region Calculate Price
    @staticmethod
    async def _calculate_room_price(
        session: AsyncSession,
        room: Room,
        guest_quantity: int,
    ) -> float:
        if not room.use_dinamic_price:
            return room.base_price

        dynamic_price = await RoomPriceDAO.get_room_price_by_guest_quantity(
            session=session,
            room_id=room.id,
            guest_quantity=guest_quantity,
        )

        # Если не удалось получить динамическую цену, возвращаем базовую
        if dynamic_price.price is None:
            logger.warning(
                f"Failed to get dynamic price, using base price: {room.base_price}"
            )
            return room.base_price

        logger.info(f"Using dynamic price: {dynamic_price}")
        return dynamic_price.price

    # endregion
    # region Get Booked Rooms
    @classmethod
    async def get_booked_rooms_count_by_hotel_id(
        cls,
        session: AsyncSession,
        check_in_date: date,
        check_out_date: date,
        hotel_id: int,
    ) -> dict[int, int]:
        """
        Возвращает словарь, где ключ - ID комнаты, значение - количество забронированных комнат
        """

        # Создаем запрос для подсчета количества бронирований для каждой комнаты
        booked_rooms_count_stmt = (
            select(BookedRoom.room_id, func.count(BookedRoom.id).label("booking_count"))
            .join(Booking, Booking.id == BookedRoom.booking_id)
            .join(Room, Room.id == BookedRoom.room_id)
            .where(
                Room.hotel_id == hotel_id,
                Booking.status == BookingStatus.BOOKED,
                or_(
                    and_(
                        Booking.check_in_date <= check_in_date,
                        Booking.check_out_date > check_in_date,
                    ),
                    and_(
                        Booking.check_in_date < check_out_date,
                        Booking.check_out_date >= check_out_date,
                    ),
                    and_(
                        Booking.check_in_date >= check_in_date,
                        Booking.check_out_date <= check_out_date,
                    ),
                ),
            )
            .group_by(BookedRoom.room_id)
        )

        result = await session.execute(booked_rooms_count_stmt)
        booked_rooms_count = {room_id: count for room_id, count in result.all()}
        return booked_rooms_count

    # endregion
    # region Check Room
    @staticmethod
    async def is_room_available(
        session: AsyncSession,
        room: Room,
        check_in_date: date,
        check_out_date: date,
        guest_quantity: int,
    ) -> bool:
        """
        Проверяет, доступна ли конкретная комната для заданных дат и количества гостей.
        """
        # Получаем словарь с количеством забронированных комнат для отеля
        booked_rooms_count = await BookingDAO.get_booked_rooms_count_by_hotel_id(
            session=session,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            hotel_id=room.hotel_id,
        )
        current_booked_count = booked_rooms_count.get(room.id, 0)
        room_quantity = getattr(room, "quantity", 1)

        # Проверка: если комната полностью забронирована
        if current_booked_count >= room_quantity:
            return False

        # Проверка: если количество гостей превышает допустимое
        if guest_quantity > room.max_guests:
            return False

        return True

    # endregion
    # region by Hotel ID
    @classmethod
    async def get_bookings_by_hotel_id(
        cls,
        session: AsyncSession,
        hotel_id: int,
        page: int,
        page_size: int,
    ):
        offset = (page - 1) * page_size
        count_query = select(func.count()).select_from(
            select(Booking).where(Booking.hotel_id == hotel_id).subquery()
        )
        total_count = await session.execute(count_query)
        total = total_count.scalar_one()
        query = (
            select(Booking)
            .options(
                selectinload(Booking.booking_rooms)
                .joinedload(BookedRoom.room)
                .joinedload(Room.room_type)
                .load_only(
                    RoomType.name,
                ),
                joinedload(Booking.user).load_only(
                    User.id,
                    User.first_name,
                    User.last_name,
                    User.phone_number,
                ),
                joinedload(Booking.payment_method).load_only(
                    PaymentMethod.name,
                ),
            )
            .where(Booking.hotel_id == hotel_id)
            .order_by(Booking.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await session.execute(query)
        bookings = result.scalars().all()
        formatted_bookings = []
        for booking in bookings:
            booking_data = {
                "id": booking.id,
                "status": booking.status,
                "check_in_date": booking.check_in_date,
                "check_out_date": booking.check_out_date,
                "total_price": booking.total_price,
                "total_days": booking.total_days,
                "special_requests": booking.special_requests,
                "payment_method": booking.payment_method.name,
                "booking_type": booking.booking_type,
                "time": booking.time,
                "user_id": booking.user_id,
                "created_at": booking.created_at,
                "total_guests": booking.total_guests,
                "user": {
                    "id": booking.user.id,
                    "first_name": booking.user.first_name,
                    "last_name": booking.user.last_name,
                    "phone_number": booking.user.phone_number,
                },
                "rooms_count": (
                    len(booking.booking_rooms) if booking.booking_rooms else 0
                ),
                "booking_rooms": [
                    {
                        "room_id": br.room_id,
                        "guest_name": br.guest_name,
                        "guest_quantity": br.guest_quantity,
                        "room_price": br.room_price,
                        "room_type": (
                            br.room.room_type.name if br.room.room_type else None
                        ),
                    }
                    for br in booking.booking_rooms
                ],
            }
            formatted_bookings.append(booking_data)
        return formatted_bookings

    # endregion
    # region Prepare for Redis
    @classmethod
    async def prepare_booking_data_for_redis(
        cls,
        session: AsyncSession,
        booking_data: BookingInitialCreate,
        user_id: int,
        hotel_id: int,
    ) -> dict:
        """Подготовка данных для бронирования"""
        logger.info(f"Preparing booking data for hotel {hotel_id}")
        # проверка на корректность дат
        if booking_data.check_in_date >= booking_data.check_out_date:
            raise BadRequestException(
                detail="Check-out date must be after check-in date"
            )
        total_price = 0
        total_days = (booking_data.check_out_date - booking_data.check_in_date).days
        # Проверяем доступность комнат
        await cls.check_rooms_availability(
            session=session,
            check_in_date=booking_data.check_in_date,
            check_out_date=booking_data.check_out_date,
            hotel_id=hotel_id,
            rooms_info=booking_data.rooms_info,
        )
        # Расчет общей стоимости
        processed_rooms_info = []
        for room_info in booking_data.rooms_info:
            db_room = await RoomDAO.get_one_or_none(
                session=session,
                filters=RoomFilter(
                    id=room_info.room_id,
                    hotel_id=hotel_id,
                ),
            )

            # Расчет цены
            room_price = await cls._calculate_room_price(
                session,
                db_room,
                room_info.guest_quantity,
            )
            room_type = await RoomTypeDAO.get_one_or_none(
                session=session,
                filters=RoomTypeFilter(
                    id=db_room.room_type_id,
                ),
            )
            processed_room = RoomInfoCreateInternal(
                uuid=str(uuid_pkg.uuid4()),
                room_id=room_info.room_id,
                guest_quantity=room_info.guest_quantity,
                price=room_price,
                type=room_type.name if room_type else None,
            )
            processed_rooms_info.append(processed_room.model_dump())

            room_total_price = total_days * room_price
            total_price += room_total_price
        booking_create_data = BookingInitialCreateInternal(
            check_in_date=booking_data.check_in_date,
            check_out_date=booking_data.check_out_date,
            total_days=total_days,
            total_price=total_price,
            hotel_id=hotel_id,
            user_id=user_id,
            uuid=str(uuid_pkg.uuid4()),
            rooms_info=processed_rooms_info,
        )

        logger.info(f"Prepared booking data: {booking_create_data}")
        return booking_create_data

    # endregion
    # region Create  in Redis
    @classmethod
    async def create_booking_in_redis(
        cls,
        booking_data: BookingInitialCreateInternal,
    ) -> str:
        """Создание временного бронирования в Redis"""

        # booking_create = booking_data.model_dump()
        booking_id = await redis_booking.add_booking(booking_data)

        logger.info(f"Created temporary booking in Redis with ID: {booking_id}")
        return booking_id

    @classmethod
    async def get_bookings_by_user_id(
        cls,
        session: AsyncSession,
        user_id: int,
    ):
        query = (
            select(Booking)
            .options(
                selectinload(Booking.booking_rooms)
                .selectinload(BookedRoom.room)
                .selectinload(Room.room_images),
                selectinload(Booking.booking_rooms)
                .selectinload(BookedRoom.room)
                .joinedload(Room.room_type),
            )
            .where(Booking.user_id == user_id)
            .order_by(Booking.created_at.desc())
        )
        result = await session.execute(query)
        bookings = result.scalars().all()
        # Получаем информацию о всех отелях для бронирований
        formatted_bookings = []
        if not bookings:
            return formatted_bookings
        hotel_ids = {booking.hotel_id for booking in bookings}
        hotel_query = (
            select(Hotel)
            .where(Hotel.id.in_(hotel_ids))
            .options(
                selectinload(Hotel.hotel_images),
                selectinload(Hotel.location)
                .joinedload(HotelLocation.city)
                .load_only(City.name),
            )
        )
        hotels = await session.execute(hotel_query)
        hotels_dict = {hotel.id: hotel for hotel in hotels.scalars().all()}
        for booking in bookings:
            booking_data = {
                "id": booking.id,
                "status": booking.status,
                "check_in_date": booking.check_in_date,
                "check_out_date": booking.check_out_date,
                "total_price": booking.total_price,
                "total_days": booking.total_days,
                "special_requests": (
                    booking.special_requests if booking.special_requests else None
                ),
                "payment_method_id": booking.payment_method_id,
                "booking_type": booking.booking_type,
                "time": booking.time if booking.time else None,
                "hotel_id": booking.hotel_id,
                "user_id": booking.user_id,
                "created_at": booking.created_at,
                "booking_rooms": [
                    await cls._serialize_booking_room(
                        booking_room=br,
                        room=br.room,
                    )
                    for br in booking.booking_rooms
                ],
                "hotel_info": None,
            }

            hotel = hotels_dict.get(booking.hotel_id)
            if hotel:
                booking_data["hotel_info"] = {
                    "id": hotel.id,
                    "name": hotel.name,
                    "slug": hotel.slug,
                    "description": hotel.description,
                    "hotel_category_id": hotel.hotel_category_id,
                    "hotel_admin_id": hotel.hotel_admin_id,
                    "images": hotel.hotel_images,
                    "location": {
                        "id": hotel.location.id if hotel.location else None,
                        "address": hotel.location.address if hotel.location else None,
                        "city": (
                            hotel.location.city.name
                            if hotel.location and hotel.location.city
                            else None
                        ),
                        "latitude": hotel.location.latitude if hotel.location else None,
                        "longitude": (
                            hotel.location.longitude if hotel.location else None
                        ),
                        "to_airport": (
                            hotel.location.to_airport if hotel.location else None
                        ),
                        "to_railway": (
                            hotel.location.to_railway if hotel.location else None
                        ),
                        "to_city_center": (
                            hotel.location.to_city_center if hotel.location else None
                        ),
                    },
                }
            formatted_bookings.append(booking_data)
        return formatted_bookings

    # endregion
    # region Serialize Booking Room
    @classmethod
    async def _serialize_booking_room(
        cls,
        booking_room: BookedRoom,
        room: Room,
    ) -> dict:
        return {
            "room_id": booking_room.room_id,
            "guest_name": booking_room.guest_name,
            "guest_quantity": booking_room.guest_quantity,
            "price": booking_room.room_price,
            "room_type": room.room_type.name if room.room_type else None,
            "images": room.room_images,
        }

    # endregion
    # region Get User Completed
    @classmethod
    async def get_user_completed_bookings(
        cls,
        session: AsyncSession,
        user_id: int,
        hotel_id: int,
        current_date: date,
    ) -> list:
        """
        Получает список завершенных бронирований пользователя в указанном отеле
        Бронь считается завершенной, если дата выезда меньше текущей даты
        """
        bookings = await session.execute(
            select(Booking).where(
                Booking.user_id == user_id,
                Booking.hotel_id == hotel_id,
                Booking.check_out_date < current_date,
                Booking.status == BookingStatus.COMPLETED,
            )
        )
        return bookings.scalars().all()

    # endregion
    # region Active Bookings
    @classmethod
    async def get_booked_rooms_by_dates(
        cls,
        session: AsyncSession,
        start_date: date,
        end_date: date,
        hotel_id: int,
    ) -> dict:
        """
        Возвращает данные о бронированиях комнат с разбивкой по датам в указанном диапазоне
        """
        if start_date > end_date:
            raise BadRequestException(
                error_code=ErrorCode.BAD_REQUEST,
                detail="Start date must be before end date",
            )

        # Получаем бронирования, которые пересекаются с указанным периодом
        bookings_query = (
            select(
                Booking.id,
                Booking.check_in_date,
                Booking.check_out_date,
                BookedRoom.room_id,
                Room.room_type_id,
                RoomType.name.label("room_type_name"),
            )
            .join(BookedRoom, Booking.id == BookedRoom.booking_id)
            .join(Room, BookedRoom.room_id == Room.id)
            .join(RoomType, Room.room_type_id == RoomType.id)
            .where(
                Room.hotel_id == hotel_id,
                Booking.status == BookingStatus.BOOKED,
                # Добавляем фильтрацию по датам - бронирования, которые
                # пересекаются с указанным периодом
                or_(
                    and_(
                        Booking.check_in_date <= end_date,
                        Booking.check_out_date > start_date,
                    )
                ),
            )
            .order_by(Room.id)
        )

        bookings_result = await session.execute(bookings_query)
        bookings = bookings_result.all()
        logger.info(
            f"Найдено {len(bookings)} бронирований, пересекающихся с указанным периодом"
        )

        # Получаем уникальные комнаты
        rooms_query = (
            select(Room.id, RoomType.name.label("room_type_name"))
            .join(RoomType, Room.room_type_id == RoomType.id)
            .where(Room.hotel_id == hotel_id)
            .order_by(Room.id)
        )

        rooms_result = await session.execute(rooms_query)
        rooms = rooms_result.all()

        # Считаем общее количество комнат
        total_rooms_query = select(func.count()).select_from(
            select(Room.id).where(Room.hotel_id == hotel_id).distinct().subquery()
        )
        total_rooms_result = await session.execute(total_rooms_query)
        total_rooms = total_rooms_result.scalar_one()

        # Формируем результат
        result_data = []
        for room_id, room_type_name in rooms:
            room_bookings = {}

            # Находим бронирования для этой комнаты
            for booking in bookings:
                if booking.room_id == room_id:
                    # Определяем диапазон дат для обработки
                    booking_start = max(booking.check_in_date, start_date)
                    booking_end = min(booking.check_out_date, end_date)

                    # Разбиваем диапазон дат на отдельные дни
                    current_date = booking_start
                    while current_date <= booking_end:
                        date_str = current_date.isoformat()
                        if date_str not in room_bookings:
                            room_bookings[date_str] = {
                                "booking_id": booking.id,
                                "check_in_date": date_str,
                                "count": 1,
                            }
                        else:
                            room_bookings[date_str]["count"] += 1

                        current_date = current_date + timedelta(days=1)

            # Добавляем информацию о комнате в результат
            result_data.append(
                {
                    "room_id": room_id,
                    "room_type": room_type_name,
                    "active_bookings": list(room_bookings.values()),
                }
            )

        return {
            "data": result_data,
            "total": total_rooms,
        }

    # endregion
