import asyncio
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db_helper
from app.core.config import SOURCE_DIR
from app.core.logger import logging
from app.dao.hotel.amenities import HotelAmenityCategoryDAO, HotelAmenityDAO
from app.dao.room.amenities import RoomAmenityCategoryDAO, RoomAmenityDAO
from app.schemas.hotel.amenities import (
    HotelAmenityCategoryCreateInternal,
    HotelAmenityCreateInternal,
)
from app.schemas.room.amenities import (
    RoomAmenityCategoryCreate,
    RoomAmenityCreateInternal,
)

logger = logging.getLogger(__name__)


async def create_amenities(
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
        for category_item in hotel_amenities_data:
            try:
                existing_category = await HotelAmenityCategoryDAO.get_one_or_none_by_id(
                    session=session,
                    data_id=category_item["id"],
                )

                if existing_category:
                    logger.info(
                        f"Категория с названием '{category_item['category_name']['ru']}' уже существует, пропускаем"
                    )
                    continue
                hotel_amenity_category_create = HotelAmenityCategoryCreateInternal(
                    name=category_item["category_name"],
                )
                created_hotel_amenity_category = await HotelAmenityCategoryDAO.create(
                    session=session,
                    values=hotel_amenity_category_create,
                )

                for hotel_amenity_name in category_item["amenities"]:
                    try:
                        existing_amenity = await HotelAmenityDAO.get_one_or_none_by_id(
                            session=session,
                            data_id=hotel_amenity_name["id"],
                        )

                        if existing_amenity:
                            logger.info(
                                f"Удобство с названием '{hotel_amenity_name['name']['ru']}' уже существует, пропускаем"
                            )
                            continue
                        hotel_amenity_create = HotelAmenityCreateInternal(
                            name=hotel_amenity_name["name"],
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
                    f"Failed to add category {category_item['category_name']['ru']}: {e}"
                )
                continue
        # Create room amenities
        for category_item in room_amenities_data:
            try:
                existing_category = await RoomAmenityCategoryDAO.get_one_or_none_by_id(
                    session=session,
                    data_id=category_item["id"],
                )

                if existing_category:
                    logger.info(
                        f"Категория с названием '{category_item['category_name']['ru']}' уже существует, пропускаем"
                    )
                    continue
                room_amenity_category_create = RoomAmenityCategoryCreate(
                    name=category_item["category_name"],
                )
                created_room_amenity_category = await RoomAmenityCategoryDAO.create(
                    session=session,
                    values=room_amenity_category_create,
                )

                for room_amenity_name in category_item["amenities"]:
                    try:
                        existing_amenity = await RoomAmenityDAO.get_one_or_none_by_id(
                            session=session,
                            data_id=room_amenity_name["id"],
                        )

                        if existing_amenity:
                            logger.info(
                                f"Удобство комнат с названием '{room_amenity_name['name']['ru']}' уже существует, пропускаем"
                            )
                            continue
                        room_amenity_create = RoomAmenityCreateInternal(
                            name=room_amenity_name["name"],
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
                    f"Failed to add category {category_item['category_name']['ru']}: {e}"
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
        await create_amenities(session)
        logger.info("Database population completed")


if __name__ == "__main__":
    asyncio.run(main())
