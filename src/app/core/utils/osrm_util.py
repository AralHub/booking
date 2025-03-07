import aiohttp

from app.api.locations.schemas import (
    Coordinates,
    DistanceResponse,
    RoutePoint,
    RouteRequest,
    RouteResponse,
    RouteSegment,
)


class OSRMDistanceCalculator:
    """
    async def example_usage():
    # Create sample points
    points = [
        RoutePoint(
            coordinates=Coordinates(
                longitude=13.375253677368166, latitude=52.54358145411929
            ),
            name="Point A",
        ),
        RoutePoint(
            coordinates=Coordinates(
                longitude=13.403406143188478, latitude=52.531939622327705
            ),
            name="Point B",
        ),
    ]

    # Create route request
    request = RouteRequest(points=points)

    # Initialize calculator
    calculator = OSRMDistanceCalculator()

    try:
        # Calculate route
        response = await calculator.calculate_distance(request)

        print(f"Total distance: {response.total_distance:.2f} meters")
        print(f"Total duration: {response.total_duration:.2f} seconds")

        for i, segment in enumerate(response.segments, 1):
            print(f"\nSegment {i}:")
            print(f"From: {segment.start_point.name}")
            print(f"To: {segment.end_point.name}")
            print(f"Distance: {segment.distance:.2f} meters")
            print(f"Duration: {segment.duration:.2f} seconds")

    except Exception as e:
        print(f"Error: {e}")
    """

    def __init__(self, base_url: str = "http://router.project-osrm.org"):
        self.base_url = base_url.rstrip("/")

    async def _make_request(self, coordinates: str) -> dict:
        url = f"{self.base_url}/route/v1/driving/{coordinates}?steps=false"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise ValueError(
                        f"OSRM API error: {response.status} - {await response.text()}"
                    )
                return await response.json()

    async def calculate_distance(self, route_request: RouteRequest) -> RouteResponse:
        if len(route_request.points) < 2:
            raise ValueError("At least 2 points are required to calculate distance")

        coordinates = route_request.get_coordinates_string()
        route_data = await self._make_request(coordinates)

        if not route_data.get("routes"):
            raise ValueError("No route found")

        route = route_data["routes"][0]
        segments = []

        # Create segments for each consecutive pair of points
        for i in range(len(route_request.points) - 1):
            segment = RouteSegment(
                start_point=route_request.points[i],
                end_point=route_request.points[i + 1],
                distance=route["legs"][i]["distance"],
                duration=route["legs"][i]["duration"],
            )
            segments.append(segment)

        return RouteResponse(
            segments=segments,
            total_distance=route["distance"],
            total_duration=route["duration"],
        )

    async def calculate_distance_between_points(
        self, point_a: Coordinates, point_b: Coordinates
    ) -> DistanceResponse:
        """
        Расчет расстояния между двумя точками через OSRM API

        Args:
            point_a: Координаты первой точки
            point_b: Координаты второй точки

        Returns:
            DistanceResponse: Модель с расстоянием и длительностью маршрута
        """

        points = [
            RoutePoint(coordinates=point_a, name="point A"),
            RoutePoint(coordinates=point_b, name="point B"),
        ]

        request = RouteRequest(points=points)
        response = await self.calculate_distance(request)

        return DistanceResponse(
            distance=response.total_distance, duration=response.total_duration
        )


distance_calculator = OSRMDistanceCalculator()
