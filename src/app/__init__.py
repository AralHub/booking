from fastapi import APIRouter

from app.auth.models import TokenBlacklist, User
from app.auth.routes.auth_router import router as auth_router
from app.auth.routes.user_router import router as user_router
from app.core.config import settings

main_router = APIRouter(
    prefix=settings.api.prefix,
)
main_router.include_router(
    auth_router,
)
main_router.include_router(
    user_router,
    prefix=settings.api_v1.prefix,
)
