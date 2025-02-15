import json

from app.core.logger import logging
from app.create_fastapi_app import redis_client
from app.schemas.order import OrderCreateInternal

logger = logging.getLogger(__name__)


ORDER_EXPIRATION_TIME = 3600  # 1 час


async def get_order_data(key: str):
    data = await redis_client.client.get(key)
    if data:
        logger.info(f"Order data fetched from Redis: {data}")
        return OrderCreateInternal.model_validate(json.loads(data))
    return None


async def add_order(order: OrderCreateInternal):
    document = order.model_dump_json()
    order_id = str(order.uuid)
    await redis_client.client.setex(order_id, ORDER_EXPIRATION_TIME, document)
    logger.info(f"Order added to Redis: {order_id}")
    return order_id
