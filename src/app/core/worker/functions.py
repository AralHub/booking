import asyncio

# import logging
import uvloop
from arq.worker import Worker

from app.core.logger import logging

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


# logging.basicConfig(
#     level=settings.logging_config.LOG_LEVEL,
#     format=settings.logging_config.LOG_FORMAT,
# )

logger = logging.getLogger(__name__)


# -------- background tasks --------
async def sample_background_task(ctx: Worker, name: str) -> str:
    await asyncio.sleep(5)
    logging.info(f"Executing task with name: {name}")  # Добавим лог для отслеживания
    return f"Task {name} is complete!"


async def startup(ctx: Worker) -> None:
    logging.info("Worker Started")


# -------- base functions --------
# async def startup(ctx: Worker) -> None:
#     logging.info("Worker Started")


async def shutdown(ctx: Worker) -> None:
    logging.info("Worker end")
