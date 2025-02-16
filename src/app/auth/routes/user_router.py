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


@router.post(
    "/profile/",
)
async def create_profile(
    request: Request,
):
    pass


@router.patch("/phone-number/")
async def change_phone_number():
    pass


@router.post("/phone-number/verify/")
async def verify_phone_number():
    pass


@router.delete(
    "/{user_id}",
)
async def auth_user_delete():
    pass
