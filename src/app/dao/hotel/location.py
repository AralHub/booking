from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.location import CityDAO
from app.dao import BaseDAO
from app.core.exceptions.http_exceptions import NotFoundException

from app.models.hotel.location import HotelLocation
from app.schemas.hotel.location import (
    Coordinates,
    LocationCreate,
    LocationCreateInternal,
    RoutePoint,
)


class LocationDAO(BaseDAO):
    model = HotelLocation

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
        # hotel_point = RoutePoint(
        #     coordinates=Coordinates(
        #         longitude=location_create_data.longitude,
        #         latitude=location_create_data.latitude,
        #     ),
        #     name="hotel_coordinates",
        # )
        # # Расчет расстояний отдельно
        # to_airport_request = RouteRequest(
        #     points=[
        #         hotel_point,
        #         RoutePoint(
        #             coordinates=Coordinates(
        #                 longitude=db_city.aero_lng, latitude=db_city.aero_lat
        #             ),
        #             name="city_airport_coordinates",
        #         ),
        #     ]
        # )
        # to_airport = await distance_calculator.calculate_distance(to_airport_request)
        # to_railway_request = RouteRequest(
        #     points=[
        #         hotel_point,
        #         RoutePoint(
        #             coordinates=Coordinates(
        #                 longitude=db_city.rail_lng, latitude=db_city.rail_lat
        #             ),
        #             name="city_railway_coordinates",
        #         ),
        #     ]
        # )
        # to_railway = await distance_calculator.calculate_distance(to_railway_request)
        # to_city_center_request = RouteRequest(
        #     points=[
        #         hotel_point,
        #         RoutePoint(
        #             coordinates=Coordinates(
        #                 longitude=db_city.center_lng, latitude=db_city.center_lat
        #             ),
        #             name="city_center_coordinates",
        #         ),
        #     ]
        # )
        # to_city_center = await distance_calculator.calculate_distance(
        #     to_city_center_request
        # )

        return await LocationDAO.create(
            session=session,
            values=LocationCreateInternal(
                **location_create_data.model_dump(),
                # to_airport=to_airport.total_distance,
                # to_railway=to_railway.total_distance,
                # to_city_center=to_city_center.total_distance,
                hotel_id=hotel_id,
            ),
        )

    @staticmethod
    def create_route_point(name, lat, lng):
        return RoutePoint(
            coordinates=Coordinates(longitude=lng, latitude=lat),
            name=name,
        )
