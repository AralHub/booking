from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.location import CityDAO
from app.dao import BaseDAO
from app.core.exceptions.http_exceptions import NotFoundException
from app.core.utils.osrm_util import distance_calculator
from app.models.hotel.location import HotelLocation
from app.schemas.location import (
    Coordinates,
    RoutePoint,
)
from app.schemas.hotel.location import (
    LocationCreate,
    LocationCreateInternal,
    LocationUpdate,
    LocationUpdateInternal,
)


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
                longitude=float(db_city.aero_geocode_lng),
                latitude=float(db_city.aero_geocode_lat),
            ),
            name="airport_coordinates",
        )
        to_airport = await distance_calculator.calculate_distance_between_points(
            hotel_point.coordinates, airport_point.coordinates
        )

        # Calculate distance to railway station
        railway_point = RoutePoint(
            coordinates=Coordinates(
                longitude=float(db_city.rail_geocode_lng),
                latitude=float(db_city.rail_geocode_lat),
            ),
            name="railway_coordinates",
        )
        to_railway = await distance_calculator.calculate_distance_between_points(
            hotel_point.coordinates, railway_point.coordinates
        )

        # Calculate distance to city center
        center_point = RoutePoint(
            coordinates=Coordinates(
                longitude=float(db_city.geocode_lng),
                latitude=float(db_city.geocode_lat),
            ),
            name="center_coordinates",
        )
        to_center = await distance_calculator.calculate_distance_between_points(
            hotel_point.coordinates, center_point.coordinates
        )
        return (
            to_airport.distance,
            to_railway.distance,
            to_center.distance,
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
                await cls.calculate_all_distances(hotel_point, db_city)
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
        db_hotel_location = await cls.get_one_or_none_by_id(
            session=session, data_id=hotel_id
        )
        if not db_hotel_location:
            raise NotFoundException("Hotel location not found")
        return await cls.update(
            session=session, data_id=hotel_id, values=location_update_data
        )
