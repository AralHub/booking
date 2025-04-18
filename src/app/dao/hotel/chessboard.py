from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions.http_exceptions import BadRequestException
from app.core.i18n.translations import ErrorCode

from app.dao import BaseDAO
from app.dao.room import RoomDAO
from app.models.hotel.chessboard import ChessBoard
from app.schemas.hotel.chessboard import (
    ChessBoardCreate,
    ChessBoardUpdate,
    ChessBoardCreateInternal,
    ChessBoardFilter,
)
from app.models.room import Room


class ChessBoardDAO(BaseDAO):
    model = ChessBoard

    @classmethod
    async def get_chessboard_items(
        cls,
        session: AsyncSession,
        hotel_id: int,
    ):
        query = (
            select(cls.model)
            .options(
                selectinload(
                    cls.model.room,
                )
            )
            .where(
                cls.model.hotel_id == hotel_id,
            )
        )
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def create_chessboard_item(
        cls,
        session: AsyncSession,
        room_id: int,
        create_data: ChessBoardCreate,
    ):
        available_rooms_count = create_data.available_rooms_count
        db_room = await RoomDAO.get_hotel_room_by_id(
            session=session,
            room_id=room_id,
        )
        if not db_room:
            raise BadRequestException(
                error_code=ErrorCode.NOT_FOUND,
            )
        if available_rooms_count > db_room.get("quantity"):
            raise BadRequestException(
                error_code=ErrorCode.BAD_REQUEST,
            )
        created_chessboard_item = await cls.create(
            session=session,
            values=ChessBoardCreateInternal(
                **create_data.model_dump(),
                hotel_id=db_room.get("hotel_id"),
                room_id=room_id,
            ),
        )
        return created_chessboard_item

    @classmethod
    async def update_chessboard_item(
        cls,
        session: AsyncSession,
        update_data: ChessBoardUpdate,
        room_id: int,
        hotel_id: int,
    ):
        updated_chessboard_item = await cls.get_one_or_none(
            session=session,
            filters=ChessBoardFilter(
                available_rooms_count=update_data.available_rooms_count,
                check_date=update_data.check_date,
                room_id=room_id,
                hotel_id=hotel_id,
            ),
        )
        return updated_chessboard_item
