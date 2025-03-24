import uvicorn
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import router as api_v1_router
from app.core.config import settings
from app.core.exceptions.http_exceptions import CustomException
from app.core.i18n.translations import get_error_message
from app.core.logger import logging
from app.create_fastapi_app import create_app

logger = logging.getLogger(__name__)

main_app = create_app()

main_app.include_router(
    api_v1_router,
    prefix=settings.api.prefix,
)


@main_app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    """Глобальный обработчик для всех исключений, наследующихся от CustomException"""
    language = getattr(request.state, "language", "ru")

    error_code = getattr(exc, "error_code", None)

    if error_code:
        detail = get_error_message(
            error_code,
            language,
        )
    else:
        detail = exc.detail

    content = {
        "status": "error",
        "detail": detail,
    }
    if error_code:
        content["error_code"] = error_code

    return JSONResponse(
        status_code=exc.status_code,
        content=content,
    )


main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене замените на конкретные домены
    allow_credentials=True,  # Важно для работы с куками
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.HOST,
        port=settings.run.PORT,
        reload=True,
    )
