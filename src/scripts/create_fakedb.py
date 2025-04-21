import asyncio
import json
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db_helper
from app.core.config import SOURCE_DIR
from app.core.logger import logging
from app.core.utils.slug_utils import generate_slug_for_hotel
from app.dao.hotel import HotelDAO
from app.dao.room import RoomDAO
from app.dao.room.amenities import RoomAmenityDAO
from app.schemas.hotel import HotelFullCreateInternal
from app.schemas.room import RoomCreate

logger = logging.getLogger(__name__)


async def create_hotels(session: AsyncSession):
    try:
        # Загружаем данные из JSON
        with open(f"{SOURCE_DIR}/scripts/sample_data/fake_db.json", encoding="utf-8") as file:
            hotels_data = json.load(file)

        for hotel in hotels_data["hotels"]:
            try:
                generated_slug = await generate_slug_for_hotel(
                    session=session,
                    name=hotel["name_en"],
                )
                hotel_create = HotelFullCreateInternal(
                    address=hotel["address"],
                    city_id=hotel["city_id"],
                    created_at=datetime.now(UTC),
                    description_en=hotel["description_en"],
                    description_kk=hotel["description_kk"],
                    description_ru=hotel["description_ru"],
                    description_uz=hotel["description_uz"],
                    amenities=hotel["facilities"],
                    hotel_admin_id=1,
                    hotel_category_id=hotel["hotel_category_id"],
                    information_for_booking=hotel["information_for_booking"],
                    information_for_guests=hotel["information_for_guests"],
                    latitude=hotel["latitude"],
                    longitude=hotel["longitude"],
                    name_en=hotel["name_en"],
                    name_kk=hotel["name_kk"],
                    name_ru=hotel["name_ru"],
                    name_uz=hotel["name_uz"],
                    slug=generated_slug,
                )
                created_hotel = await HotelDAO.create_new_hotel(
                    session=session,
                    hotel_create_data=hotel_create,
                    hotel_admin_id=hotel["hotel_admin_id"],
                )
                logger.info(f"Successfully created hotel: {hotel['name_en']}")
                for hotel_room in hotel["rooms"]:
                    created_room = await RoomDAO.add_room_to_hotel(
                        session=session,
                        hotel_id=created_hotel.id,
                        room_data=RoomCreate(
                            quantity=hotel_room["quantity"],
                            base_price=hotel_room["base_price"],
                            room_area=hotel_room["room_area"],
                            max_guests=hotel_room["max_guests"],
                            room_type_id=hotel_room["room_type_id"],
                        ),
                    )
                    (
                        await RoomAmenityDAO.add_amenities_to_room(
                            session=session,
                            amenities=hotel_room["room_amenities"],
                            room_id=created_room.id,
                        ),
                    )

            except Exception as e:
                logger.error(f"Failed to create hotel {hotel['name_en']}: {e}")

        await session.commit()
        logger.info("All hotels created successfully")

    except Exception as e:
        logger.error(f"Failed to create hotels: {e}")
        await session.rollback()
        raise


async def main():
    async with db_helper.session_factory() as session:
        await create_hotels(session)
        logger.info("Database population completed")


if __name__ == "__main__":
    asyncio.run(main())
