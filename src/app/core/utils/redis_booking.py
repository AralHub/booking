import json

from app.core.logger import logging
from app.create_fastapi_app import redis_client
from app.schemas.booking import BookingCreateInternal

logger = logging.getLogger(__name__)


ORDER_EXPIRATION_TIME = 300  # 5 minutes


async def get_booking_data(key: str):
    data = await redis_client.client.get(key)
    if data:
        logger.info(f"Order data fetched from Redis: {data}")
        return BookingCreateInternal.model_validate(json.loads(data))
    return None


async def add_booking(booking: BookingCreateInternal):
    document = booking.model_dump_json()
    booking_id = str(booking.uuid)
    await redis_client.client.setex(booking_id, ORDER_EXPIRATION_TIME, document)
    logger.info(f"Order added to Redis: {booking_id}")
    return booking_id
