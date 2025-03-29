from datetime import date
from sqlalchemy import func, select, and_, or_
from sqlalchemy.types import Integer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions.http_exceptions import BadRequestException, NotFoundException
from app.dao import BaseDAO
from app.dao.room import RoomDAO
from app.dao.room.price import RoomPriceDAO
from app.dao.user import UserDAO
from app.models.booking import Booking, BookingStatus
from app.models.room import Room
from app.models.user import User
from app.schemas.room.price import RoomPriceFilter
from app.models.booking import Booking, BookingStatus
from app.schemas.booking import (
    BookingCreateMultipleRooms,
    BookingCreateMultipleRoomsInternal,
)
from app.models.booking import BookedRoom


class BookedRoomDAO(BaseDAO):
    model = BookedRoom


class BookingDAO(BaseDAO):
    model = Booking

    @classmethod
    async def create_booking(
        cls,
        session: AsyncSession,
        booking_data: BookingCreateMultipleRooms,
        user_id: int,
    ):
        # проверка на корректность дат
        if booking_data.check_in_date >= booking_data.check_out_date:
            raise BadRequestException(
                detail="Check-out date must be after check-in date"
            )

        # общее количество дней
        total_days = (booking_data.check_out_date - booking_data.check_in_date).days

        # Инициализация переменных
        total_price = 0
        validated_rooms_info = []

        # Получаем первую комнату для определения отеля
        first_room = await RoomDAO.get_one_or_none_by_id(
            session=session,
            data_id=booking_data.rooms_info[0].room_id,
        )
        if not first_room:
            raise NotFoundException("First room not found")

        hotel_id = first_room.hotel_id

        # Получаем все пересекающиеся бронирования для отеля
        booked_room_ids = await RoomDAO.get_booked_rooms_by_hotel_id(
            session=session,
            check_in_date=booking_data.check_in_date,
            check_out_date=booking_data.check_out_date,
            hotel_id=hotel_id,
        )

        # Проверяем каждую комнату
        for room_info in booking_data.rooms_info:
            # Проверка доступности комнаты
            if room_info.room_id in booked_room_ids:
                raise BadRequestException(
                    f"Room {room_info.room_id} is already booked for these dates"
                )

            db_room = await RoomDAO.get_one_or_none_by_id(
                session=session,
                data_id=room_info.room_id,
            )
            if not db_room:
                raise NotFoundException(f"Room with ID {room_info.room_id} not found")

            # Проверка количества гостей
            if room_info.guest_quantity > db_room.max_guests:
                raise BadRequestException(
                    f"Room {room_info.room_id} can only accommodate {db_room.max_guests} guests"
                )

            # Расчет цены
            room_price = await cls._calculate_room_price(
                session,
                db_room,
                room_info.guest_quantity,
            )

            room_total_price = total_days * room_price
            total_price += room_total_price

            # Добавляем проверенную информацию о комнате
            validated_room = room_info.model_dump()
            validated_room["price"] = room_price
            validated_room["total_price"] = room_total_price
            validated_rooms_info.append(validated_room)

        # Создаем бронирование
        booking = await cls.create(
            session=session,
            values=BookingCreateMultipleRoomsInternal(
                check_in_date=booking_data.check_in_date,
                check_out_date=booking_data.check_out_date,
                rooms_info=validated_rooms_info,
                total_days=total_days,
                total_price=total_price,
                user_id=user_id,
                special_requests=getattr(booking_data, "special_requests", None),
                hotel_id=hotel_id,
                status=BookingStatus.PENDING,
            ),
        )

        # Создаем записи о забронированных комнатах
        for room_info in validated_rooms_info:
            await BookedRoomDAO.create(
                session=session,
                values={
                    "booking_id": booking.id,
                    "room_id": room_info["room_id"],
                    "guest_quantity": room_info["guest_quantity"],
                    "price": room_info["price"],
                },
            )

        return booking

    @staticmethod
    async def _calculate_room_price(
        session: AsyncSession, room: Room, guest_quantity: int
    ) -> float:
        if room.use_dinamic_price:
            db_room_prices = await RoomPriceDAO.get_all(
                session=session,
                filters=RoomPriceFilter(room_id=room.id),
            )
            if not db_room_prices:
                return room.base_price

            return await RoomPriceDAO.get_room_price_by_guest_quantity(
                session=session,
                room_id=room.id,
                guest_quantity=guest_quantity,
            )
        return room.base_price
