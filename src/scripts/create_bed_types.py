import asyncio
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.room.dao import BedTypeDAO
from app.api.room.schemas import BedFilter
from app.core import db_helper
from app.core.config import SOURCE_DIR
from app.core.logger import logging

logger = logging.getLogger(__name__)


async def create_fake_db(
    session: AsyncSession,
):
    try:
        BED_TYPES_JSON_PATH = f"{SOURCE_DIR}/scripts/sample_data/bed_types.json"

        with open(BED_TYPES_JSON_PATH, encoding="utf-8") as file:
            bed_types_data = json.load(file)

        # Create hotel categories
        for bed_type in bed_types_data["bed_types"]:
            try:
                bed_type_create = BedFilter(
                    id=bed_type["id"],
                    name=bed_type["name"],
                )
                await BedTypeDAO.create(
                    session=session,
                    values=bed_type_create,
                )
            except Exception as e:
                logger.error(f"Failed to add category {bed_type.get('name')}: {e}")
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
