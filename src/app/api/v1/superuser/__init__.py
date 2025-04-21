# from app.api.v1.superuser.auth import router as auth_router
from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(
    tags=["Superuser"],
    prefix=settings.api_v1.superuser_prefix,
)

# router.include_router(auth_router)
