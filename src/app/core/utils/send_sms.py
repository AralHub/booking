from app.core.config import settings
from app.core.exceptions.http_exceptions import TooManyRequestsException
from app.core.utils import redis_sms, task_queue


async def send_verification_sms(phone_number: str) -> tuple[bool, str]:
    code = "12345"
    # code = await code_generator()
    success, message = await redis_sms.save_sms_code(
        phone=phone_number,
        code=code,
    )
    if not success:
        raise TooManyRequestsException(message)
    message = f"{settings.eskiz.ESKIZ_TEMPLATE_TEXT} {code}"
    # await task_queue.pool.enqueue_job(
    #     "send_sms_task",
    #     message=message,
    #     phone_number=user_phone_number.phone_number,
    # )
    await task_queue.pool.enqueue_job(
        "send_sms_code",
        message=message,
        phone_number=phone_number,
    )
    return True, "SMS sent successfully"
