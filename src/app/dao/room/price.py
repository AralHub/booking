from sqlalchemy.ext.asyncio import AsyncSession
from app.core.i18n.translations import ErrorCode
from app.core.exceptions.http_exceptions import NotFoundException, BadRequestException
from app.dao import BaseDAO
from app.models.room.price import RoomPrice
from app.schemas.room.price import (
    RoomPriceFilter,
    RoomPriceCreate,
    RoomPriceCreateInternal,
)


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

    @classmethod
    async def create_room_prices(
        cls,
        session: AsyncSession,
        room_id: int,
        prices: list[RoomPriceCreate],
        max_guests: int,
    ):
        for price in prices:
            if price.guest_quantity > max_guests:
                raise BadRequestException(
                    error_code=ErrorCode.BAD_REQUEST,
                )
            room_price_create_data = RoomPriceCreateInternal(
                room_id=room_id,
                **price.model_dump(
                    exclude_unset=True,
                ),
            )
            await RoomPriceDAO.create(
                session=session,
                values=room_price_create_data,
            )

    @classmethod
    async def delete_room_all_prices(
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
            return
        await cls.delete_many(
            session=session,
            ids=[room_price.id for room_price in room_prices],
        )
