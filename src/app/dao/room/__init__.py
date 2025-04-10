from datetime import date
from sqlalchemy import and_, func, or_, select, case, text, literal_column, table
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions.http_exceptions import (
    NotFoundException,
    BadRequestException,
)
from app.dao import BaseDAO
from app.models.booking import Booking, BookingStatus
from app.dao.room.price import RoomPriceDAO
from app.models.room import Room
from app.models.room.price import RoomPrice
from app.models.room.types import RoomType
from app.models.booking import BookedRoom
from app.schemas.booking import BookedRoomCreate
from app.schemas.room import (
    RoomCreateInternal,
    RoomCreate,
    RoomUpdate,
    RoomUpdateInternal,
    RoomFilter,
)
from app.schemas.room.types import RoomTypeFilter
import logging

logger = logging.getLogger(__name__)


class RoomTypeDAO(BaseDAO):
    model = RoomType


class RoomDAO(BaseDAO):
    model = Room

    @classmethod
    async def add_room_to_hotel(
        cls,
        session: AsyncSession,
        room_data: RoomCreate,
        hotel_id: int,
    ):
        db_room_type = await RoomTypeDAO.get_one_or_none(
            session=session,
            filters=RoomTypeFilter(
                id=room_data.room_type_id,
            ),
        )
        if not db_room_type:
            raise NotFoundException(
                detail="Room type not found",
            )
        hotel_room_create_data = RoomCreateInternal(
            **room_data.model_dump(),
            hotel_id=hotel_id,
        )
        return await cls.create(
            session=session,
            values=hotel_room_create_data,
        )

    @classmethod
    async def update_hotel_room(
        cls,
        session: AsyncSession,
        room_data: RoomUpdate,
        room_id: int,
        hotel_id: int,
    ):
        # Проверяем существование room_type если он указан
        if room_data.room_type_id is not None:
            room_type = await RoomTypeDAO.get_one_or_none(
                session=session,
                filters=RoomTypeFilter(
                    id=room_data.room_type_id,
                ),
            )
            if not room_type:
                raise NotFoundException("Room type does not exist")
        updated_row_count = await RoomDAO.update(
            session=session,
            values=RoomUpdateInternal(
                **room_data.model_dump(
                    exclude_none=True,
                    exclude_unset=True,
                )
            ),
            filters=RoomFilter(
                id=room_id,
                hotel_id=hotel_id,
            ),
        )
        if updated_row_count == 0 or updated_row_count is None:
            raise NotFoundException("Room did not update")
        return {
            "message": "Room updated successfully",
        }

    @classmethod
    async def get_booked_rooms_by_hotel_id(
        cls,
        session: AsyncSession,
        check_in_date: date,
        check_out_date: date,
        hotel_id: int,
    ):
        # Получаем все активные бронирования на указанные даты
        booked_rooms_stmt = (
            select(BookedRoom.room_id, func.count().label("booked_count"))
            .join(Booking)
            .where(
                and_(
                    Room.hotel_id == hotel_id,
                    Booking.status == BookingStatus.BOOKED,
                    or_(
                        # Scenario 1: booking starts before check-in and ends after
                        and_(
                            Booking.check_in_date <= check_in_date,
                            Booking.check_out_date > check_in_date,
                        ),
                        # Scenario 2: booking starts before check-out and ends after
                        and_(
                            Booking.check_in_date < check_out_date,
                            Booking.check_out_date >= check_out_date,
                        ),
                        # Scenario 3: booking completely within requested period
                        and_(
                            Booking.check_in_date >= check_in_date,
                            Booking.check_out_date <= check_out_date,
                        ),
                    ),
                )
            )
            .group_by(BookedRoom.room_id)
        )
        booked_rooms_result = await session.execute(booked_rooms_stmt)
        booked_rooms = booked_rooms_result.all()
        return {room_id: count for room_id, count in booked_rooms}

    @classmethod
    async def get_available_rooms(
        cls,
        session: AsyncSession,
        hotel_id: int,
        check_in_date: date,
        check_out_date: date,
        guests: list[int],
    ):
        booked_rooms_dict = await cls.get_booked_rooms_by_hotel_id(
            session=session,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            hotel_id=hotel_id,
        )
        print(booked_rooms_dict)
        available_rooms_stmt = (
            select(
                Room,
                RoomType.name.label("room_type_name"),
                RoomType.description.label("room_type_description"),
            )
            .join(RoomType, Room.room_type_id == RoomType.id)
            .where(Room.hotel_id == hotel_id)
        )
        available_rooms_result = await session.execute(available_rooms_stmt)

        available_rooms = available_rooms_result.all()
        rooms_data = []

        for room, room_type_name, room_type_description in available_rooms:
            # Проверяем доступное количество номеров
            booked_count = booked_rooms_dict.get(room.id, 0)
            available_quantity = room.quantity - booked_count

            # Пропускаем номер, если все экземпляры забронированы
            if available_quantity <= 0:
                continue

            # Получаем цену на указанный период
            price = await RoomPriceDAO.get_room_price(
                session=session,
                room_id=room.id,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
            )
            room_data = {
                "id": room.id,
                "name": room.name,
                "quantity": room.quantity,
                "available_quantity": available_quantity,
                "description": room.description,
                "max_guests": room.max_guests,
                "room_type_id": room.room_type_id,
                "room_type_name": room_type_name,
                "room_type_description": room_type_description,
                "base_price": room.base_price,
                "actual_price": price,
            }
        rooms_data.append(room_data)

        # Находим подходящие комнаты для размещения гостей
        suitable_rooms = cls._find_suitable_rooms_for_guests(
            available_rooms=rooms_data,
            guests=guests,
        )
        return suitable_rooms

    @classmethod
    def _find_suitable_rooms_for_guests(
        cls,
        available_rooms: list[dict],
        guests: list[int],
    ):

        # Копия списка гостей для манипуляций
        remaining_guests = guests.copy()
        remaining_guests.sort(reverse=True)

        # Копия доступных номеров для отслеживания использования
        rooms_to_use = []
        available_rooms_copy = []

        for room in available_rooms:
            # Добавляем каждый номер столько раз, сколько у него доступных экземпляров
            for _ in range(room["available_quantity"]):
                available_rooms_copy.append(room.copy())

        # Сортируем номера по убыванию максимального количества гостей
        available_rooms_copy.sort(key=lambda x: x["max_guests"], reverse=True)

        all_guests_accommodated = True
        for group_size in remaining_guests:
            room_found = False

            for i, room in enumerate(available_rooms_copy):
                if room["max_guests"] >= group_size:
                    rooms_to_use.append(room)
                    available_rooms_copy.pop(i)
                    room_found = True
                    break

            if not room_found:
                all_guests_accommodated = False
                break

        if not all_guests_accommodated:
            return None

        return rooms_to_use
