import asyncio
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db_helper
from app.core.config import SOURCE_DIR
from app.core.logger import logging
from app.dao.hotel import HotelCategoryDAO
from app.schemas.hotel.category import HotelCategoryCreateInternal

logger = logging.getLogger(__name__)


async def create_hotel_categories(
    session: AsyncSession,
):
    try:
        HOTEL_CATEGORIES_JSON_PATH = (
            f"{SOURCE_DIR}/scripts/sample_data/hotel_categories.json"
        )

        with open(HOTEL_CATEGORIES_JSON_PATH, encoding="utf-8") as file:
            hotel_categories_data = json.load(file)

        # Create hotel categories
        for hotel_category_item in hotel_categories_data["hotel_categories"]:
            try:
                hotel_category_create = HotelCategoryCreateInternal(
                    name=hotel_category_item["name"],
                    description=hotel_category_item["description"],
                )
                await HotelCategoryDAO.create(
                    session=session,
                    values=hotel_category_create,
                )
            except Exception as e:
                logger.error(
                    f"Failed to add category {hotel_category_item.get('name')["ru"]}: {e}"
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
        await create_hotel_categories(session)
        logger.info("Database population completed")


if __name__ == "__main__":
    asyncio.run(main())
