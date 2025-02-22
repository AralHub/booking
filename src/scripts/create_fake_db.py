import asyncio
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.locations.dao import CityDAO, CountryDAO
from app.api.locations.schemas import CityFilter, CountryFilter

# from app.api.amenities.dao import HotelAmenityCategoryDAO, HotelAmenityDAO
# from app.api.amenities.schemas import HotelAmenityCategoryFilter, HotelAmenityFilter
from app.core import db_helper
from app.core.config import SOURCE_DIR
from app.core.logger import logging

logger = logging.getLogger(__name__)


async def create_fake_db(
    session: AsyncSession,
):
    try:
        CITIES_JSON_PATH = f"{SOURCE_DIR}/scripts/sample_data/cities.json"
        # AMENITIES_JSON_PATH = f"{SOURCE_DIR}/scripts/sample_data/hotel_amenities.json"
        with open(CITIES_JSON_PATH, encoding="utf-8") as file:
            fake_data = json.load(file)
        # with open(AMENITIES_JSON_PATH, encoding="utf-8") as file:
        #     amenities_data = json.load(file)
        logger.info("Creating country...")
        country_create = CountryFilter(
            id=1,
            name="Uzbekistan",
            code="UZ",
        )
        country = await CountryDAO.create(
            session=session,
            values=country_create,
        )

        logger.info("Creating cities...")
        for city_data in fake_data:
            try:
                city_create = CityFilter(
                    id=city_data["id"],
                    name=city_data["name"],
                    slug=city_data["slug"],
                    properties_count=city_data["properties_count"],
                    image=city_data["image"],
                    aero_lat=float(city_data["aero_geocode_lat"]),
                    aero_lng=float(city_data["aero_geocode_lng"]),
                    rail_lat=float(city_data["rail_geocode_lat"]),
                    rail_lng=float(city_data["rail_geocode_lng"]),
                    country_id=country.id,
                )
                await CityDAO.create(
                    session=session,
                    values=city_create,
                )
            except Exception as e:
                logger.error(
                    f"Failed to add city {city_data.get('name', 'unknown')}: {e}"
                )
                continue
        # for category_name, amenities in amenities_data.items():
        #     try:
        #         category_create = AmenityCategoryFilter(
        #             name=category_name,
        #         )
        #         category = await AmenityCategoryDAO.create(
        #             session=session,
        #             values=category_create,
        #         )

        #         for amenity_name in amenities:
        #             try:
        #                 amenity_create = AmenityFilter(
        #                     name=amenity_name,
        #                     category_id=category.id,
        #                 )
        #                 await AmenityDAO.create(
        #                     session=session,
        #                     values=amenity_create,
        #                 )
        #             except Exception as e:
        #                 logger.error(f"Failed to add amenity {amenity_name}: {e}")
        #                 continue
        #     except Exception as e:
        #         logger.error(f"Failed to add category {category_name}: {e}")
        #         continue
        logger.info("Committing transaction...")
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
