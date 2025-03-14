from collections.abc import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logger import logging

logger = logging.getLogger(__name__)


class LanguageMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ):
        try:
            return await call_next(request)

        except Exception as e:
            logging.error(f"Server error: {str(e)}", exc_info=True)
            raise
