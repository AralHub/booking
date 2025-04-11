from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BaseDAO
from app.core.exceptions.http_exceptions import NotFoundException
from app.schemas.room.price import RoomPriceFilter
from app.models.room.price import RoomPrice
from app.core.i18n.translations import ErrorCode


class RoomPriceDAO(BaseDAO):
    model = RoomPrice

    @classmethod
    async def get_room_prices(
        cls,
        session: AsyncSession,
        room_id: int,
    ):
        room_prices = await cls.get_all(
            session=session,
            filters=RoomPriceFilter(
                room_id=room_id,
            ),
        )
        if not room_prices:
            raise NotFoundException(
                detail="Room prices not found",
                error_code=ErrorCode.ROOM_PRICE_NOT_FOUND,
            )
        return room_prices

    @classmethod
    async def get_room_price(
        cls,
        session: AsyncSession,
        room_id: int,
    ):
        room_price = await cls.get_one_or_none(
            session=session,
            filters=RoomPriceFilter(
                room_id=room_id,
            ),
        )
        if not room_price:
            return None
        return room_price

    @classmethod
    async def get_room_price_by_guest_quantity(
        cls,
        session: AsyncSession,
        room_id: int,
        guest_quantity: int,
    ):
        room_price_data = await cls.get_one_or_none(
            session=session,
            filters=RoomPriceFilter(
                room_id=room_id,
                guest_quantity=guest_quantity,
            ),
        )
        return room_price_data.price if room_price_data else None
