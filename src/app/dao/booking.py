from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions.http_exceptions import BadRequestException, NotFoundException
from app.dao import BaseDAO
from app.dao.room import RoomDAO
from app.dao.room.price import RoomPriceDAO
from app.models.booking import Booking, BookingStatus
from app.models.room import Room
from app.schemas.room.price import RoomPriceFilter
from app.schemas.room import RoomFilter
from app.models.booking import Booking, BookingStatus
from app.schemas.booking import (
    BookingCreateMultipleRooms,
    BookingCreateMultipleRoomsInternal,
    BookedRoomCreateInternal,
)
from app.models.booking import BookedRoom
from sqlalchemy import select, and_, or_


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
        hotel_id: int,
    ):
        # проверка на корректность дат
        if booking_data.check_in_date >= booking_data.check_out_date:
            raise BadRequestException(
                detail="Check-out date must be after check-in date"
            )
        total_price = 0
        total_days = (booking_data.check_out_date - booking_data.check_in_date).days
        # Получаем все пересекающиеся бронирования для отеля
        booked_room_ids = await RoomDAO.get_booked_rooms_by_hotel_id(
            session=session,
            check_in_date=booking_data.check_in_date,
            check_out_date=booking_data.check_out_date,
            hotel_id=hotel_id,
        )

        # Проверяем каждую комнату
        for room in booking_data.rooms_info:
            # Проверка доступности комнаты
            if room.room_id in booked_room_ids:
                raise BadRequestException(
                    f"Room {room.room_id} is already booked for these dates"
                )

            db_room = await RoomDAO.get_one_or_none(
                session=session,
                filters=RoomFilter(
                    id=room.room_id,
                    hotel_id=hotel_id,
                ),
            )
            if not db_room:
                raise NotFoundException(f"Room with ID {room.room_id} not found")

            # Проверка количества гостей
            if room.guest_quantity > db_room.max_guests:
                raise BadRequestException(
                    f"Room {room.room_id} can only accommodate {db_room.max_guests} guests"
                )

            # Расчет цены
            room_price = await cls._calculate_room_price(
                session,
                db_room,
                room.guest_quantity,
            )

            room_total_price = total_days * room_price
            total_price += room_total_price

        # Создаем бронирование
        booking_create_data = BookingCreateMultipleRoomsInternal(
            check_in_date=booking_data.check_in_date,
            check_out_date=booking_data.check_out_date,
            total_days=total_days,
            total_price=total_price,
            special_requests=getattr(booking_data, "special_requests", None),
            hotel_id=hotel_id,
            status=BookingStatus.BOOKED,
            user_id=user_id,
        )
        crated_booking = await cls.create(
            session=session,
            values=booking_create_data,
        )
        for room in booking_data.rooms_info:
            await BookedRoomDAO.create(
                session=session,
                values=BookedRoomCreateInternal(
                    booking_id=crated_booking.id,
                    room_id=room.room_id,
                    guest_quantity=room.guest_quantity,
                    guest_name=room.guest_name,
                ),
            )

        return crated_booking

    @staticmethod
    async def _calculate_room_price(
        session: AsyncSession,
        room: Room,
        guest_quantity: int,
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

    @classmethod
    async def get_bookings_by_hotel_ids(
        cls,
        session: AsyncSession,
        hotel_ids: list[int],
        check_in_date: date,
        check_out_date: date,
    ):
        booked_rooms_stmt = (
            select(BookedRoom.room_id)
            .join(Booking, Booking.id == BookedRoom.booking_id)
            .join(Room)  # Добавляем join с таблицей rooms
            .where(
                Room.hotel_id.in_(hotel_ids),  # Используем in_ для списка ID
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
        )

        return (await session.execute(booked_rooms_stmt)).scalars().all()
