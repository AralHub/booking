import asyncio
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.room.dao import RoomTypeDAO, RoomTypeVariantDAO
from app.api.room.schemas import RoomTypeCreateInternal, RoomTypeVariantCreateInternal
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
                    name=room_type["name"],
                )
                room_type_db = await RoomTypeDAO.create(
                    session=session,
                    values=room_type_create,
                )
                # Создаем варианты комнаты
                for variant_name in room_type["room_type_variants"]:
                    logger.info(
                        f"Current variant_name: {variant_name}"
                    )  # Log variant name
                    room_create = RoomTypeVariantCreateInternal(
                        name=variant_name,
                        room_type_id=room_type_db.id,
                    )  # используем room_type.id
                    await RoomTypeVariantDAO.create(
                        session=session,
                        values=room_create,
                    )

            except Exception as e:
                logger.error(
                    f"Failed to add room type or variant {room_type.get('name', 'N/A')}: {e}"
                )
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
