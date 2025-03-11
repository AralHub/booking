from fastapi import APIRouter

from app.api.v1.partner import router as partner_router
from app.api.v1.user import (
    router as user_router,
)
from app.api.v1.user.superuser import (
    router as superuser_router,
)
from app.core.config import settings

router = APIRouter(
    prefix=settings.api_v1.prefix,
)

router.include_router(
    user_router,
)
router.include_router(
    partner_router,
)
router.include_router(
    superuser_router,
)
