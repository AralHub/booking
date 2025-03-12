from fastapi import APIRouter

from app.core.config import settings

from .hotel import router as hotel_router
from .partner import router as partner_router
from .room import router as room_router
from .superuser import router as superuser_router
from .superuser.hotel.amenities import router as hotel_amenities_router
from .superuser.hotel.category import router as hotel_category_router
from .superuser.room.amenities import router as room_amenities_router
from .superuser.room.types import router as room_types_router
from .user import router as user_router

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
    hotel_router,
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
