import json

from app.core.logger import logging
from app.create_fastapi_app import redis_client
from app.schemas.booking import BookingInitialCreate, BookingInitialRead

logger = logging.getLogger(__name__)


EXPIRATION_TIME = 600  # 10 minutes


async def get_booking_data(key: str):
    data = await redis_client.client.get(key)
    if data:
        logger.info(f"Booking data fetched from Redis: {data}")
        return BookingInitialRead.model_validate(json.loads(data))
    return None


async def add_booking(booking: BookingInitialCreate):
    document = booking.model_dump_json()
    booking_id = str(booking.uuid)
    await redis_client.client.setex(booking_id, EXPIRATION_TIME, document)
    logger.info(f"Booking added to Redis: {booking_id}")
    return booking_id
