from fastapi import APIRouter

from app.core.config import settings

from .booking import router as booking_router
from .hotel import router as hotel_router
from .hotel.amenities import router as amenities_router
from .hotel.images import router as images_router
from .hotel.info import router as info_router
from .hotel.location import router as location_router
from .hotel.review import router as review_router
from .hotel.rules import router as rules_router
from .location import router as superuser_location_router
from .partner import router as partner_router
from .room import router as room_router
from .superuser import router as superuser_router
from .superuser.hotel.amenities import router as hotel_amenities_router
from .superuser.hotel.category import router as hotel_category_router
from .superuser.review import router as superuser_review_router
from .superuser.room.amenities import router as room_amenities_router
from .superuser.room.types import router as room_types_router
from .user import router as user_router
from .user.favorites import router as favorites_router

router = APIRouter(
    prefix=settings.api_v1.prefix,
)

router.include_router(
    user_router,
)
router.include_router(
    partner_router,
)
router.include_router(
    favorites_router,
)
router.include_router(
    booking_router,
)
router.include_router(
    hotel_router,
)
router.include_router(
    location_router,
)
router.include_router(
    info_router,
)
router.include_router(
    rules_router,
)
router.include_router(
    amenities_router,
)
router.include_router(
    images_router,
)
router.include_router(
    review_router,
)
router.include_router(
    room_router,
)
router.include_router(
    superuser_router,
)
router.include_router(
    hotel_amenities_router,
)
router.include_router(
    hotel_category_router,
)
router.include_router(
    room_amenities_router,
)
router.include_router(
    room_types_router,
)
router.include_router(
    superuser_review_router,
)
router.include_router(
    superuser_location_router,
)
