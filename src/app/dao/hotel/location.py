from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao.location import CityDAO
from app.dao import BaseDAO
from app.core.exceptions.http_exceptions import NotFoundException
from app.core.utils.osrm_util import distance_calculator
from app.models.hotel.location import HotelLocation
from app.schemas.location import (
    Coordinates,
    RoutePoint,
    RouteRequest,
)
from app.schemas.hotel.location import (
    LocationCreate,
    LocationCreateInternal,
    LocationUpdate,
    LocationUpdateInternal,
    LocationFilter,
    LocationRead,
)
from app.models.location import City


class HotelLocationDAO(BaseDAO):
    model = HotelLocation

    @staticmethod
    async def calculate_all_distances(
        hotel_point: RoutePoint,
        db_city,
    ) -> tuple:

        # Calculate distance to airport
        airport_point = RoutePoint(
            coordinates=Coordinates(
                longitude=db_city.aero_lng,
                latitude=db_city.aero_lat,
            ),
            name="airport_coordinates",
        )
        airport_request = RouteRequest(points=[hotel_point, airport_point])
        to_airport = await distance_calculator.calculate_distance(airport_request)

        # Calculate distance to railway station
        railway_point = RoutePoint(
            coordinates=Coordinates(
                longitude=db_city.rail_lng,
                latitude=db_city.rail_lat,
            ),
            name="railway_coordinates",
        )
        railway_request = RouteRequest(points=[hotel_point, railway_point])
        to_railway = await distance_calculator.calculate_distance(railway_request)

        # Calculate distance to city center
        center_point = RoutePoint(
            coordinates=Coordinates(
                longitude=db_city.geocode_lng,
                latitude=db_city.geocode_lat,
            ),
            name="center_coordinates",
        )
        center_request = RouteRequest(points=[hotel_point, center_point])
        to_center = await distance_calculator.calculate_distance(center_request)

        return (
            to_airport.total_distance,
            to_railway.total_distance,
            to_center.total_distance,
        )

    @classmethod
    async def add_hotel_location(
        cls,
        session: AsyncSession,
        location_create_data: LocationCreate,
        hotel_id: int,
    ):
        db_city = await CityDAO.get_one_or_none_by_id(
            session=session,
            data_id=location_create_data.city_id,
        )
        if not db_city:
            raise NotFoundException("City not found")
        # Создаем точку отеля
        hotel_point = RoutePoint(
            coordinates=Coordinates(
                longitude=location_create_data.longitude,
                latitude=location_create_data.latitude,
            ),
            name="hotel_coordinates",
        )
        try:
            to_airport_distance, to_railway_distance, to_center_distance = (
                await cls.calculate_all_distances(
                    hotel_point,
                    db_city,
                )
            )

            return await HotelLocationDAO.create(
                session=session,
                values=LocationCreateInternal(
                    **location_create_data.model_dump(
                        exclude_none=True,
                        exclude_unset=True,
                    ),
                    to_airport=to_airport_distance,
                    to_railway=to_railway_distance,
                    to_city_center=to_center_distance,
                    hotel_id=hotel_id,
                ),
            )
        except Exception as e:
            return await HotelLocationDAO.create(
                session=session,
                values=LocationCreateInternal(
                    **location_create_data.model_dump(),
                    to_airport=None,
                    to_railway=None,
                    to_city_center=None,
                    hotel_id=hotel_id,
                ),
            )

    @classmethod
    async def update_hotel_location(
        cls,
        session: AsyncSession,
        location_update_data: LocationUpdate,
        hotel_id: int,
    ):
        db_hotel_location = await cls.get_one_or_none(
            session=session,
            filters=LocationFilter(
                hotel_id=hotel_id,
            ),
        )
        if not db_hotel_location:
            raise NotFoundException("Hotel location not found")
        if location_update_data.city_id and location_update_data.city_id != 0:
            db_city = await CityDAO.get_one_or_none_by_id(
                session=session,
                data_id=location_update_data.city_id,
            )
            if not db_city:
                raise NotFoundException("City not found")
        else:
            db_city = await CityDAO.get_one_or_none_by_id(
                session=session,
                data_id=db_hotel_location.city_id,
            )
        hotel_point = RoutePoint(
            coordinates=Coordinates(
                longitude=location_update_data.longitude,
                latitude=location_update_data.latitude,
            ),
            name="hotel_coordinates",
        )
        try:
            to_airport_distance, to_railway_distance, to_center_distance = (
                await cls.calculate_all_distances(hotel_point, db_city)
            )
            return await cls.update(
                session=session,
                values=LocationUpdateInternal(
                    **location_update_data.model_dump(
                        exclude_none=True,
                        exclude_unset=True,
                    ),
                    to_airport=round(to_airport_distance / 1000, 2),
                    to_railway=round(to_railway_distance / 1000, 2),
                    to_city_center=round(to_center_distance / 1000, 2),
                ),
                filters=LocationFilter(
                    hotel_id=hotel_id,
                ),
            )
        except Exception as e:
            return await cls.update(
                session=session,
                values=LocationUpdateInternal(
                    **location_update_data.model_dump(),
                    to_airport=None,
                    to_railway=None,
                    to_city_center=None,
                ),
            )

    @classmethod
    async def get_hotel_location(cls, session: AsyncSession, hotel_id: int):
        query = (
            select(cls.model, City.name.label("city"))
            .where(cls.model.hotel_id == hotel_id)
            .join(City, City.id == cls.model.city_id)
        )
        result = await session.execute(query)
        db_result = result.one_or_none()

        if db_result:
            location, city_name = db_result

            return LocationRead.from_orm_with_city(location, city_name)
        return None
