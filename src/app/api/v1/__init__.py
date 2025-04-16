from fastapi import APIRouter

from app.core.config import settings

from .booking import router as booking_router
from .favorites import router as favorites_router
from .hotel import router as hotel_router
from .hotel.amenities import router as hotel_amenities_router
from .hotel.chessboard import router as hotel_chessboard_router
from .hotel.images import router as hotel_images_router
from .hotel.info import router as hotel_info_router
from .hotel.location import router as hotel_location_router
from .hotel.rating import router as hotel_rating_router
from .hotel.review import router as hotel_review_router
from .hotel.rules import router as hotel_rules_router
from .partner import router as partner_router
from .room import router as room_router
from .room.bed import router as room_bed_router
from .room.images import router as room_images_router
from .room.price import router as room_price_router
from .superuser import router as superuser_router
from .superuser.hotel import router as superuser_hotel_router
from .superuser.hotel.amenities import router as superuser_hotel_amenities_router
from .superuser.hotel.category import router as superuser_hotel_category_router

# from .room.amenities import router as room_amenities_router
from .superuser.location import router as superuser_location_router
from .superuser.payment import router as superuser_payment_router
from .superuser.review import router as superuser_review_router
from .superuser.room.amenities import router as superuser_room_amenities_router
from .superuser.room.types import router as superuser_room_types_router
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
    favorites_router,
)
router.include_router(
    booking_router,
)
router.include_router(
    hotel_chessboard_router,
)
router.include_router(
    hotel_router,
)
router.include_router(
    hotel_location_router,
)
router.include_router(
    hotel_info_router,
)
router.include_router(
    hotel_rules_router,
)
router.include_router(
    hotel_amenities_router,
)
router.include_router(
    hotel_images_router,
)
router.include_router(
    hotel_review_router,
)
router.include_router(
    hotel_rating_router,
)
router.include_router(
    room_router,
)
# router.include_router(
#     room_amenities_router,
# )
router.include_router(
    room_images_router,
)
router.include_router(
    room_price_router,
)
router.include_router(
    room_bed_router,
)
router.include_router(
    superuser_router,
)
router.include_router(
    superuser_hotel_router,
)
router.include_router(
    superuser_hotel_amenities_router,
)
router.include_router(
    superuser_hotel_category_router,
)
router.include_router(
    superuser_room_amenities_router,
)
router.include_router(
    superuser_room_types_router,
)
router.include_router(
    superuser_review_router,
)
router.include_router(
    superuser_location_router,
)
router.include_router(
    superuser_payment_router,
)
