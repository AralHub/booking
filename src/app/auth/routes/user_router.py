from fastapi import APIRouter, Request

from app.core.config import settings

# from app.core.utils.eskiz_client import code_generator

router = APIRouter(
    tags=["User"],
    prefix=settings.api_v1.user_prefix,
)


@router.get(
    "/me/",
)
async def get_me(
    request: Request,
):
    pass
