from arq import cron
from arq.connections import RedisSettings

from ..config import settings
from .functions import (
    check_restaurant_is_expired,
    sample_background_task,
    send_sms_code_sample,
    send_sms_task,
    shutdown,
    startup,
)


class WorkerSettings:
    functions = [
        sample_background_task,
        send_sms_code_sample,
        send_sms_task,
    ]
    redis_settings = RedisSettings(
        host=settings.redis_client.REDIS_HOST,
        port=settings.redis_client.REDIS_PORT,
    )
    on_startup = startup
    on_shutdown = shutdown
    handle_signals = False
