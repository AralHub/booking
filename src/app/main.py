import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from app import main_router
from app.core.config import settings
from app.core.logger import logging
from app.create_fastapi_app import create_app

logger = logging.getLogger(__name__)

main_app = create_app()

main_app.include_router(main_router)
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
