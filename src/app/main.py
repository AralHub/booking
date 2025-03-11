import uvicorn
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import router as api_v1_router
from app.core.config import settings
from app.core.logger import logging
from app.create_fastapi_app import create_app
from app.middleware.error_handle_middleware import ErrorHandleMiddleware

logger = logging.getLogger(__name__)


main_app = create_app()

main_app.include_router(
    api_v1_router,
    prefix=settings.api.prefix,
)


@main_app.exception_handler(Exception)
async def internal_exception_handler(
    request: Request,
    exc: Exception,
):
    # Log the error details (without exposing internal information to the client)
    logging.error(f"Unhandled error occurred: {exc}", exc_info=True)

    # Return a generic error response
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error. Please try again later."},
    )


main_app.add_middleware(ErrorHandleMiddleware)
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
