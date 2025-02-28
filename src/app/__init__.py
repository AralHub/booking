from fastapi import APIRouter

from app.api.user.models import TokenBlacklist, User
from app.api.hotel.models import Hotel
from app.api.hotel_admin.models import HotelAdmin
from app.api.images.models import HotelImage
from app.api.amenity.hotel_amenity.models import HotelAmenity, HotelAmenityAssociation
from app.api.amenity.room_amenity.models import RoomAmenity, RoomAmenityAssociation
from app.api.review.models import Review, ReviewCategory, ReviewCategoryRating
from app.api.room.models import (
    Room,
    RoomType,
)


from app.api.user.routes.user import router as user_router
from app.api.user.routes.auth import router as auth_router
from app.api.user.routes.superuser import router as superuser_router
from app.api.hotel.router import router as hotel_router
from app.api.amenity.hotel_amenity.router import router as hotel_amenity_router
from app.api.amenity.room_amenity.router import router as room_amenity_router
from app.api.booking.router import router as booking_router

# from app.api.images.router import router as image_router
from app.api.locations.router import router as location_router
from app.api.room.router import router as room_router

# from app.api.owner.router import router as owner_router

from app.core.config import settings

main_router = APIRouter(
    prefix=settings.api.prefix,
)
main_router.include_router(
    auth_router,
)
main_router.include_router(
    user_router,
    prefix=settings.api_v1.prefix,
)
main_router.include_router(
    booking_router,
    prefix=settings.api_v1.prefix,
)

main_router.include_router(
    hotel_router,
    prefix=settings.api_v1.prefix,
)
# main_router.include_router(
#     owner_router,
#     prefix=settings.api_v1.prefix,
# )
main_router.include_router(
    hotel_amenity_router,
    prefix=settings.api_v1.prefix,
)
# main_router.include_router(
#     hotel_rule_router,
#     prefix=settings.api_v1.prefix,
# )

main_router.include_router(
    room_router,
    prefix=settings.api_v1.prefix,
)
main_router.include_router(
    room_amenity_router,
    prefix=settings.api_v1.prefix,
)
# main_router.include_router(
#     image_router,
#     prefix=settings.api_v1.prefix,
# )
main_router.include_router(
    location_router,
    prefix=settings.api_v1.prefix,
)

main_router.include_router(
    superuser_router,
    prefix=settings.api_v1.prefix,
)
