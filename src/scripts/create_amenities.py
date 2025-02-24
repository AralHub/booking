import asyncio
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.amenity.hotel_amenity.dao import HotelAmenityCategoryDAO, HotelAmenityDAO
from app.api.amenity.hotel_amenity.schemas import (
    HotelAmenityCategoryFilter,
    HotelAmenityFilter,
)
from app.api.amenity.room_amenity.dao import RoomAmenityCategoryDAO, RoomAmenityDAO
from app.api.amenity.room_amenity.schemas import (
    RoomAmenityCategoryFilter,
    RoomAmenityFilter,
)
from app.core import db_helper
from app.core.config import SOURCE_DIR
from app.core.logger import logging

logger = logging.getLogger(__name__)


async def create_fake_db(
    session: AsyncSession,
):
    try:
        HOTEL_AMENITIES_JSON_PATH = (
            f"{SOURCE_DIR}/scripts/sample_data/hotel_amenities.json"
        )
        ROOM_AMENITIES_JSON_PATH = (
            f"{SOURCE_DIR}/scripts/sample_data/room_amenities.json"
        )
        with open(HOTEL_AMENITIES_JSON_PATH, encoding="utf-8") as file:
            hotel_amenities_data = json.load(file)
        with open(ROOM_AMENITIES_JSON_PATH, encoding="utf-8") as file:
            room_amenities_data = json.load(file)

        # Create hotel amenities
        for (
            hotel_amenity_category_name,
            hotel_amenities,
        ) in hotel_amenities_data.items():
            try:
                hotel_amenity_category_create = HotelAmenityCategoryFilter(
                    name=hotel_amenity_category_name,
                )
                created_hotel_amenity_category = await HotelAmenityCategoryDAO.create(
                    session=session,
                    values=hotel_amenity_category_create,
                )

                for hotel_amenity_name in hotel_amenities:
                    try:
                        hotel_amenity_create = HotelAmenityFilter(
                            name=hotel_amenity_name,
                            hotel_amenity_category_id=created_hotel_amenity_category.id,
                        )
                        await HotelAmenityDAO.create(
                            session=session,
                            values=hotel_amenity_create,
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to add hotel amenity {hotel_amenity_name}: {e}"
                        )
                        continue
            except Exception as e:
                logger.error(
                    f"Failed to add category {hotel_amenity_category_name}: {e}"
                )
                continue
        # Create room amenities
        for (
            room_amenity_category_name,
            room_amenities,
        ) in room_amenities_data.items():
            try:
                room_amenity_category_create = RoomAmenityCategoryFilter(
                    name=room_amenity_category_name,
                )
                created_room_amenity_category = await RoomAmenityCategoryDAO.create(
                    session=session,
                    values=room_amenity_category_create,
                )

                for room_amenity_name in room_amenities:
                    try:
                        room_amenity_create = RoomAmenityFilter(
                            name=room_amenity_name,
                            room_amenity_category_id=created_room_amenity_category.id,
                        )
                        await RoomAmenityDAO.create(
                            session=session,
                            values=room_amenity_create,
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to add room amenity {room_amenity_name}: {e}"
                        )
                        continue
            except Exception as e:
                logger.error(
                    f"Failed to add category {hotel_amenity_category_name}: {e}"
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
