from fastapi import APIRouter

from app.api.v1.superuser.auth import router as auth_router
from app.api.v1.superuser.hotel.amenities import router as hotel_amenities_router
from app.api.v1.superuser.hotel.category import router as hotel_category_router

# from app.api.v1.superuser.room.amenities import router as room_amenities_router
# from app.api.v1.superuser.room.types import router as room_types_router
from app.core.config import settings

router = APIRouter(
    tags=["Superuser"],
    prefix=settings.api_v1.superuser_prefix,
)

router.include_router(auth_router)
router.include_router(hotel_amenities_router)
router.include_router(hotel_category_router)
# router.include_router(room_amenities_router)
# router.include_router(room_types_router)
