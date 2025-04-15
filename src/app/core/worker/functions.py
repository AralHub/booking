import asyncio

import uvloop
from arq.worker import Worker

from app.core import db_helper
from app.core.config import settings
from app.core.logger import logging
from app.core.services.eskiz.eskiz_client import AsyncEskizClient

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logger = logging.getLogger(__name__)


# -------- background tasks --------
async def sample_background_task(ctx: Worker, name: str) -> str:
    await asyncio.sleep(5)
    logging.info(f"Executing task with name: {name}")  # Добавим лог для отслеживания
    return f"Task {name} is complete!"


async def send_sms_code_sample(
    ctx: Worker,
    message: str,
    phone_number: str,
) -> None:
    await asyncio.sleep(5)
    logging.info(f"Sendind SMS to {phone_number}")
    return f"SMS message{message} had been sent to {phone_number}"


async def send_sms_task(
    ctx: Worker,
    phone_number: str,
    message: str,
):
    try:
        client: AsyncEskizClient = ctx["eskiz_client"]
        result = await client.send_sms(phone_number, message)
        return {
            "status": "success",
            "result": result.model_dump(),
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }


# -------- base functions --------
async def startup(ctx: Worker) -> None:
    logging.info("Worker Started")
    ctx["eskiz_client"] = AsyncEskizClient(
        email=settings.eskiz.ESKIZ_EMAIL,
        password=settings.eskiz.ESKIZ_PASSWORD,
    )
    # await ctx["eskiz_client"].login()

    ctx["session"] = await anext(db_helper.session_getter())


async def shutdown(ctx: Worker) -> None:
    logging.info("Worker end")
