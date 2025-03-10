import asyncio
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.room.dao import RoomTypeDAO
from app.api.room.schemas import RoomTypeCreateInternal
from app.core import db_helper
from app.core.config import SOURCE_DIR
from app.core.logger import logging

logger = logging.getLogger(__name__)


async def create_fake_db(
    session: AsyncSession,
):
    try:
        ROOM_TYPES_JSON_PATH = f"{SOURCE_DIR}/scripts/sample_data/room_types.json"

        with open(ROOM_TYPES_JSON_PATH, encoding="utf-8") as file:
            room_types_data = json.load(file)

        # Create hotel categories
        for room_type in room_types_data["room_types"]:
            try:
                room_type_create = RoomTypeCreateInternal(
                    name=room_type,
                )
                await RoomTypeDAO.create(
                    session=session,
                    values=room_type_create,
                )

            except Exception as e:
                logger.error(f"Failed to add room type {room_type}: {e}")
                continue

        await session.commit()
        logger.info("Transaction committed successfully")

    except Exception as e:
        logger.error(f"Failed to create fake db: {e}")
        await session.rollback()
        raise


async def main():
    async with db_helper.session_factory() as session:
        await create_fake_db(session)
        logger.info("Database population completed")


if __name__ == "__main__":
    asyncio.run(main())
